"""
Tests for export functionality
"""
import pytest
import tempfile
import os
import json
import pandas as pd
from src.exports import (
    export_conversations_csv, export_findings_json,
    generate_manifest, calculate_checksum
)


def test_csv_export():
    """Test CSV export functionality"""
    df = pd.DataFrame({
        'source_id': ['TEST001', 'TEST002'],
        'customer_name': ['John Doe', 'Jane Smith'],
        'company': ['Acme', 'Beta']
    })
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp:
        output_path = tmp.name
    
    try:
        result = export_conversations_csv(df, output_path)
        
        assert result['success'] == True
        assert result['record_count'] == 2
        assert os.path.exists(output_path)
        assert 'checksum' in result
        
        # Verify file content
        exported_df = pd.read_csv(output_path)
        assert len(exported_df) == 2
        
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_json_export():
    """Test JSON export functionality"""
    findings = [
        {
            'title': 'Test Finding',
            'metric': 'Test metric',
            'recommendation': 'Test action'
        }
    ]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
        output_path = tmp.name
    
    try:
        result = export_findings_json(findings, output_path)
        
        assert result['success'] == True
        assert os.path.exists(output_path)
        
        # Verify JSON is valid
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        assert 'findings' in data
        assert len(data['findings']) == 1
        
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_manifest_generation():
    """Test manifest generation with checksums"""
    exports = [
        {
            'filename': 'test1.csv',
            'record_count': 10,
            'format': 'CSV',
            'checksum': 'abc123'
        },
        {
            'filename': 'test2.json',
            'record_count': 5,
            'format': 'JSON',
            'checksum': 'def456'
        }
    ]
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as tmp:
        output_path = tmp.name
    
    try:
        result = generate_manifest(exports, output_path)
        
        assert result['success'] == True
        assert os.path.exists(output_path)
        
        # Verify manifest content
        with open(output_path, 'r') as f:
            manifest = json.load(f)
        
        assert manifest['total_exports'] == 2
        assert len(manifest['exports']) == 2
        assert manifest['dataset_description'] == 'SYNTHETIC DEMO DATA - For demonstration purposes only'
        
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


def test_checksum_calculation():
    """Test checksum calculation"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write("test content")
        tmp_path = tmp.name
    
    try:
        checksum = calculate_checksum(tmp_path)
        
        # Should return a valid SHA-256 hash
        assert len(checksum) == 64
        assert checksum.isalnum()
        
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
