"""
Tests for data ingestion
"""
import pytest
import tempfile
import os
import pandas as pd
from src.database import Database
from src.ingestion import process_import


def test_sample_dataset_loads():
    """Test that the sample dataset loads successfully"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name
    
    try:
        db = Database(db_path)
        
        # Check if sample file exists
        sample_path = "data/sample_conversations.csv"
        if not os.path.exists(sample_path):
            pytest.skip("Sample dataset not found")
        
        result = process_import(sample_path, db)
        
        assert result['success'] == True
        assert result['stats']['new'] > 0
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_duplicate_import_prevention():
    """Test that importing the same file twice doesn't create duplicates"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name
    
    # Create temp CSV file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as csv_tmp:
        csv_path = csv_tmp.name
        csv_tmp.write("source_id,customer_name,company,stage\n")
        csv_tmp.write("TEST001,John Doe,Acme Corp,discovery\n")
        csv_tmp.write("TEST002,Jane Smith,Beta Inc,proposal\n")
    
    try:
        db = Database(db_path)
        
        # First import
        result1 = process_import(csv_path, db)
        assert result1['success'] == True
        assert result1['stats']['new'] == 2
        
        # Second import - same file
        result2 = process_import(csv_path, db)
        assert result2['success'] == True
        assert result2['stats']['unchanged'] == 2
        assert result2['stats']['new'] == 0
        
        # Verify only 2 records in database
        df = db.get_all_conversations()
        assert len(df) == 2
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(csv_path):
            os.unlink(csv_path)


def test_changed_record_updates():
    """Test that changed records update correctly"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as csv_tmp:
        csv_path = csv_tmp.name
        csv_tmp.write("source_id,customer_name,company,stage\n")
        csv_tmp.write("TEST001,John Doe,Acme Corp,discovery\n")
    
    try:
        db = Database(db_path)
        
        # First import
        result1 = process_import(csv_path, db)
        assert result1['success'] == True
        
        # Modify the CSV
        with open(csv_path, 'w') as f:
            f.write("source_id,customer_name,company,stage\n")
            f.write("TEST001,John Doe,Acme Corp,proposal\n")  # Changed stage
        
        # Second import
        result2 = process_import(csv_path, db)
        assert result2['success'] == True
        assert result2['stats']['updated'] == 1
        
        # Verify change
        conv = db.get_conversation_by_source_id('TEST001')
        assert conv['stage'] == 'proposal'
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(csv_path):
            os.unlink(csv_path)


def test_invalid_records_rejected():
    """Test that invalid records are rejected with useful errors"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as csv_tmp:
        csv_path = csv_tmp.name
        csv_tmp.write("source_id,customer_name,company,stage\n")
        csv_tmp.write(",John Doe,Acme Corp,discovery\n")  # Missing source_id
    
    try:
        db = Database(db_path)
        
        result = process_import(csv_path, db)
        
        # Should report validation errors
        assert result['success'] == False or result['stats']['failed'] > 0
        assert len(result.get('validation_errors', [])) > 0
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(csv_path):
            os.unlink(csv_path)
