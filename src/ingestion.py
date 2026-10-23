"""
Data ingestion module for SignalDesk AI
Handles CSV/Excel import with duplicate detection and change tracking
"""
import pandas as pd
from typing import Dict, List, Tuple, Any
from pathlib import Path
import hashlib

from src.database import Database
from src.validation import validate_dataframe, normalize_record
from src.routing import recommend_routing


def process_import(file_path: str, db: Database) -> Dict[str, Any]:
    """
    Process a CSV or Excel file import
    Returns import statistics and results
    """
    try:
        # Read file
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            return {
                'success': False,
                'error': 'Unsupported file format. Please use CSV or Excel (.xlsx, .xls)',
                'stats': {}
            }
        
        # Validate data
        is_valid, errors, valid_df, invalid_df = validate_dataframe(df)
        
        if len(valid_df) == 0:
            return {
                'success': False,
                'error': 'No valid records found',
                'validation_errors': errors[:20],  # Limit to first 20 errors
                'stats': {
                    'total': len(df),
                    'failed': len(df)
                }
            }
        
        # Process valid records
        stats = {
            'total': len(valid_df),
            'new': 0,
            'updated': 0,
            'unchanged': 0,
            'duplicates': 0,
            'failed': len(invalid_df)
        }
        
        # Track duplicate source_ids within the upload
        seen_source_ids = set()
        duplicate_within_file = []
        
        for idx, row in valid_df.iterrows():
            record = normalize_record(row.to_dict())
            source_id = record['source_id']
            
            # Check for duplicates within file
            if source_id in seen_source_ids:
                duplicate_within_file.append(source_id)
                stats['duplicates'] += 1
                continue
            
            seen_source_ids.add(source_id)
            
            # Check if record exists in database
            existing = db.get_conversation_by_source_id(source_id)
            
            if existing:
                # Calculate new hash
                new_hash = db.calculate_record_hash(record)
                existing_hash = existing.get('record_hash', '')
                
                # Check if record has changed
                if new_hash == existing_hash:
                    stats['unchanged'] += 1
                else:
                    # Record has changed - update if not manually overridden
                    # Apply routing if not manually set
                    if not record.get('owner') and not existing.get('manual_override') == 'TRUE':
                        routing = recommend_routing(record)
                        record['owner'] = routing['recommended_team']
                        record['priority_score'] = str(routing['priority_score'])
                        record['routing_reason'] = routing['routing_reason']
                        record['evidence_quote'] = routing['evidence_quote']
                        if not record.get('next_action'):
                            record['next_action'] = routing['next_action']
                    
                    # Update record
                    db.update_conversation(source_id, record, preserve_manual=True)
                    stats['updated'] += 1
                    
                    # Log update
                    db.log_audit_event(
                        action_type='record_updated',
                        record_id=source_id,
                        reason='CSV import update'
                    )
            else:
                # New record - apply routing
                routing = recommend_routing(record)
                record['owner'] = routing['recommended_team']
                record['priority_score'] = str(routing['priority_score'])
                record['routing_reason'] = routing['routing_reason']
                record['evidence_quote'] = routing['evidence_quote']
                if not record.get('next_action'):
                    record['next_action'] = routing['next_action']
                
                # Insert new record
                db.insert_conversation(record)
                stats['new'] += 1
                
                # Log creation
                db.log_audit_event(
                    action_type='record_created',
                    record_id=source_id,
                    reason='CSV import'
                )
        
        # Log import to history
        filename = Path(file_path).name
        db.log_import(
            filename=filename,
            stats=stats,
            status='success',
            details=f"Processed {stats['total']} records. Duplicates in file: {', '.join(duplicate_within_file) if duplicate_within_file else 'None'}"
        )
        
        return {
            'success': True,
            'stats': stats,
            'validation_errors': errors if errors else [],
            'duplicate_source_ids': duplicate_within_file
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Import failed: {str(e)}',
            'stats': {}
        }


def create_sample_template() -> pd.DataFrame:
    """Create a sample CSV template with proper structure"""
    template = pd.DataFrame({
        'source_id': ['EXAMPLE001', 'EXAMPLE002'],
        'customer_name': ['Jane Doe', 'John Smith'],
        'company': ['Example Corp', 'Sample Industries'],
        'conversation_date': ['2026-10-20', '2026-10-21'],
        'channel': ['call', 'meeting'],
        'conversation_summary': ['Discovery call about enterprise needs', 'Pricing negotiation discussion'],
        'transcript_or_notes': [
            'Customer interested in our solution. Quote: "We need a scalable platform for our growing team."',
            'Discussed pricing options. Quote: "Can you provide volume discounts for 100+ users?"'
        ],
        'sentiment': ['positive', 'neutral'],
        'deal_value': ['150000', '200000'],
        'stage': ['discovery', 'negotiation'],
        'urgency': ['medium', 'high'],
        'customer_intent': ['evaluate_solution', 'negotiate_price'],
        'objections': ['', 'price_concerns'],
        'owner': ['', ''],  # Will be auto-assigned by routing
        'status': ['', ''],
        'next_action': ['', ''],  # Will be auto-suggested
        'follow_up_date': ['2026-10-27', '2026-10-25'],
        'priority_score': ['', ''],  # Will be auto-calculated
        'routing_reason': ['', ''],
        'evidence_quote': ['', ''],
        'manual_override': ['FALSE', 'FALSE'],
        'created_at': ['', ''],
        'updated_at': ['', '']
    })
    
    return template
