"""
Export functionality for SignalDesk AI
Handles CSV, JSON exports with manifest generation and checksums
"""
import json
import hashlib
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List


def calculate_checksum(file_path: str) -> str:
    """Calculate SHA-256 checksum of a file"""
    sha256_hash = hashlib.sha256()
    
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except:
        return "ERROR: Could not calculate checksum"


def export_conversations_csv(df: pd.DataFrame, output_path: str) -> Dict[str, Any]:
    """Export conversations to CSV"""
    try:
        df.to_csv(output_path, index=False, encoding='utf-8')
        
        return {
            'success': True,
            'filename': Path(output_path).name,
            'path': output_path,
            'record_count': len(df),
            'format': 'CSV',
            'checksum': calculate_checksum(output_path)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def export_routing_decisions_csv(df: pd.DataFrame, output_path: str) -> Dict[str, Any]:
    """Export routing decisions to CSV"""
    try:
        # Select routing-specific columns
        routing_cols = [
            'source_id', 'customer_name', 'company', 'stage', 'urgency',
            'owner', 'priority_score', 'routing_reason', 'evidence_quote',
            'next_action', 'manual_override'
        ]
        
        available_cols = [col for col in routing_cols if col in df.columns]
        routing_df = df[available_cols]
        
        routing_df.to_csv(output_path, index=False, encoding='utf-8')
        
        return {
            'success': True,
            'filename': Path(output_path).name,
            'path': output_path,
            'record_count': len(routing_df),
            'format': 'CSV',
            'checksum': calculate_checksum(output_path)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def export_findings_json(findings: List[Dict[str, Any]], output_path: str) -> Dict[str, Any]:
    """Export findings to JSON"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'generated_at': datetime.now().isoformat(),
                'findings_count': len(findings),
                'findings': findings
            }, f, indent=2, ensure_ascii=False)
        
        return {
            'success': True,
            'filename': Path(output_path).name,
            'path': output_path,
            'record_count': len(findings),
            'format': 'JSON',
            'checksum': calculate_checksum(output_path)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def export_audit_log(df: pd.DataFrame, output_path: str, format: str = 'csv') -> Dict[str, Any]:
    """Export audit log to CSV or JSON"""
    try:
        if format.lower() == 'json':
            df.to_json(output_path, orient='records', indent=2)
        else:
            df.to_csv(output_path, index=False, encoding='utf-8')
        
        return {
            'success': True,
            'filename': Path(output_path).name,
            'path': output_path,
            'record_count': len(df),
            'format': format.upper(),
            'checksum': calculate_checksum(output_path)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def generate_manifest(exports: List[Dict[str, Any]], output_path: str) -> Dict[str, Any]:
    """Generate export manifest with metadata and checksums"""
    try:
        manifest = {
            'manifest_version': '1.0',
            'generated_at': datetime.now().isoformat(),
            'application': 'SignalDesk AI',
            'application_version': '1.0.0',
            'dataset_description': 'SYNTHETIC DEMO DATA - For demonstration purposes only',
            'total_exports': len(exports),
            'exports': exports
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        return {
            'success': True,
            'filename': Path(output_path).name,
            'path': output_path,
            'checksum': calculate_checksum(output_path)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
