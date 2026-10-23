"""
Tests for database module
"""
import pytest
import tempfile
import os
from src.database import Database


def test_database_initialization():
    """Test database initialization"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name
    
    try:
        db = Database(db_path)
        
        # Check that tables exist
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'conversations' in tables
        assert 'audit_log' in tables
        assert 'import_history' in tables
        
        conn.close()
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_insert_and_retrieve_conversation():
    """Test inserting and retrieving a conversation"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name
    
    try:
        db = Database(db_path)
        
        record = {
            'source_id': 'TEST001',
            'customer_name': 'Test Customer',
            'company': 'Test Corp',
            'stage': 'discovery',
            'sentiment': 'positive'
        }
        
        # Insert
        record_id = db.insert_conversation(record)
        assert record_id > 0
        
        # Retrieve
        retrieved = db.get_conversation_by_source_id('TEST001')
        assert retrieved is not None
        assert retrieved['customer_name'] == 'Test Customer'
        assert retrieved['company'] == 'Test Corp'
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_duplicate_prevention():
    """Test that duplicate source_ids are prevented"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name
    
    try:
        db = Database(db_path)
        
        record = {
            'source_id': 'DUP001',
            'customer_name': 'Duplicate Test',
            'company': 'Test Corp'
        }
        
        # First insert should succeed
        db.insert_conversation(record)
        
        # Second insert with same source_id should fail
        with pytest.raises(Exception):
            db.insert_conversation(record)
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_record_hash_calculation():
    """Test record hash calculation"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
        db_path = tmp.name
    
    try:
        db = Database(db_path)
        
        record1 = {
            'customer_name': 'John Doe',
            'company': 'Acme Corp',
            'conversation_summary': 'Test conversation'
        }
        
        record2 = {
            'customer_name': 'John Doe',
            'company': 'Acme Corp',
            'conversation_summary': 'Test conversation'
        }
        
        record3 = {
            'customer_name': 'Jane Doe',
            'company': 'Acme Corp',
            'conversation_summary': 'Test conversation'
        }
        
        hash1 = db.calculate_record_hash(record1)
        hash2 = db.calculate_record_hash(record2)
        hash3 = db.calculate_record_hash(record3)
        
        # Same content should produce same hash
        assert hash1 == hash2
        
        # Different content should produce different hash
        assert hash1 != hash3
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
