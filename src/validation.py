"""
Data validation for SignalDesk AI
Validates conversation records and CSV imports
"""
from datetime import datetime
from typing import Dict, List, Tuple, Any
import pandas as pd


REQUIRED_COLUMNS = ['source_id']

VALID_CHANNELS = ['call', 'meeting', 'email', 'other']
VALID_SENTIMENTS = ['positive', 'neutral', 'negative', 'unknown']
VALID_STAGES = ['lead', 'discovery', 'proposal', 'negotiation', 'won', 'lost', 'unknown']
VALID_URGENCIES = ['low', 'medium', 'high', 'critical']


def validate_date(date_str: str) -> Tuple[bool, str]:
    """Validate date format"""
    if not date_str or pd.isna(date_str) or str(date_str).strip() == '':
        return True, ""  # Optional field
    
    try:
        datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
        return True, ""
    except:
        try:
            pd.to_datetime(date_str)
            return True, ""
        except:
            return False, f"Invalid date format: {date_str}"


def validate_numeric(value: str, field_name: str) -> Tuple[bool, str]:
    """Validate numeric value"""
    if not value or pd.isna(value) or str(value).strip() == '' or str(value).lower() == 'unknown':
        return True, ""  # Optional or unknown
    
    try:
        float(str(value).replace(',', ''))
        return True, ""
    except:
        return False, f"Invalid numeric value for {field_name}: {value}"


def validate_record(record: Dict[str, Any], row_num: int = 0) -> Tuple[bool, List[str]]:
    """Validate a single conversation record"""
    errors = []
    
    # Check required fields
    if not record.get('source_id') or str(record.get('source_id', '')).strip() == '':
        errors.append(f"Row {row_num}: source_id is required and cannot be empty")
    
    # Validate dates
    for date_field in ['conversation_date', 'follow_up_date']:
        if date_field in record:
            valid, error = validate_date(record[date_field])
            if not valid:
                errors.append(f"Row {row_num}: {error}")
    
    # Validate deal_value
    if 'deal_value' in record:
        valid, error = validate_numeric(record['deal_value'], 'deal_value')
        if not valid:
            errors.append(f"Row {row_num}: {error}")
    
    # Validate priority_score
    if 'priority_score' in record and record['priority_score']:
        valid, error = validate_numeric(record['priority_score'], 'priority_score')
        if not valid:
            errors.append(f"Row {row_num}: {error}")
    
    # Validate categorical fields
    if record.get('channel') and record['channel'] not in VALID_CHANNELS + ['']:
        errors.append(f"Row {row_num}: Invalid channel '{record['channel']}'. Must be one of: {', '.join(VALID_CHANNELS)}")
    
    if record.get('sentiment') and record['sentiment'] not in VALID_SENTIMENTS + ['']:
        errors.append(f"Row {row_num}: Invalid sentiment '{record['sentiment']}'. Must be one of: {', '.join(VALID_SENTIMENTS)}")
    
    if record.get('stage') and record['stage'] not in VALID_STAGES + ['']:
        errors.append(f"Row {row_num}: Invalid stage '{record['stage']}'. Must be one of: {', '.join(VALID_STAGES)}")
    
    if record.get('urgency') and record['urgency'] not in VALID_URGENCIES + ['']:
        errors.append(f"Row {row_num}: Invalid urgency '{record['urgency']}'. Must be one of: {', '.join(VALID_URGENCIES)}")
    
    return len(errors) == 0, errors


def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str], pd.DataFrame, pd.DataFrame]:
    """
    Validate an entire DataFrame of conversations
    Returns: (is_valid, errors, valid_df, invalid_df)
    """
    errors = []
    
    # Check for required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {', '.join(missing_cols)}")
        return False, errors, pd.DataFrame(), df
    
    # Validate each record
    valid_indices = []
    invalid_indices = []
    
    for idx, row in df.iterrows():
        record = row.to_dict()
        is_valid, record_errors = validate_record(record, idx + 2)  # +2 for header and 0-indexing
        
        if is_valid:
            valid_indices.append(idx)
        else:
            invalid_indices.append(idx)
            errors.extend(record_errors)
    
    valid_df = df.loc[valid_indices] if valid_indices else pd.DataFrame()
    invalid_df = df.loc[invalid_indices] if invalid_indices else pd.DataFrame()
    
    return len(invalid_indices) == 0, errors, valid_df, invalid_df


def normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize and clean a record"""
    normalized = {}
    
    for key, value in record.items():
        # Handle NaN and None
        if pd.isna(value) or value is None:
            normalized[key] = ''
        else:
            # Convert to string and strip whitespace
            normalized[key] = str(value).strip()
    
    # Set defaults for boolean fields
    if 'manual_override' not in normalized or normalized['manual_override'] == '':
        normalized['manual_override'] = 'FALSE'
    
    return normalized
