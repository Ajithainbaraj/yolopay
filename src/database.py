"""
Database management for SignalDesk AI
Handles SQLite connections, schema initialization, and CRUD operations
"""
import sqlite3
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
import pandas as pd


class Database:
    def __init__(self, db_path: str = "signaldesk.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Create a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT UNIQUE NOT NULL,
                customer_name TEXT,
                company TEXT,
                conversation_date TEXT,
                channel TEXT,
                conversation_summary TEXT,
                transcript_or_notes TEXT,
                sentiment TEXT,
                deal_value TEXT,
                stage TEXT,
                urgency TEXT,
                customer_intent TEXT,
                objections TEXT,
                owner TEXT,
                status TEXT,
                next_action TEXT,
                follow_up_date TEXT,
                priority_score REAL,
                routing_reason TEXT,
                evidence_quote TEXT,
                manual_override TEXT,
                record_hash TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # Audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action_type TEXT NOT NULL,
                record_id TEXT,
                field_name TEXT,
                previous_value TEXT,
                new_value TEXT,
                reason TEXT,
                metadata TEXT
            )
        """)
        
        # Import history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS import_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                filename TEXT,
                total_records INTEGER,
                new_records INTEGER,
                updated_records INTEGER,
                unchanged_records INTEGER,
                duplicate_records INTEGER,
                failed_records INTEGER,
                status TEXT,
                details TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def calculate_record_hash(self, record: Dict[str, Any]) -> str:
        """Calculate hash of record fields (excluding metadata)"""
        # Fields that define record content (not metadata)
        content_fields = [
            'customer_name', 'company', 'conversation_date', 'channel',
            'conversation_summary', 'transcript_or_notes', 'sentiment',
            'deal_value', 'stage', 'urgency', 'customer_intent', 'objections'
        ]
        
        # Create a stable string representation
        hash_content = '|'.join([str(record.get(f, '')) for f in content_fields])
        return hashlib.sha256(hash_content.encode()).hexdigest()
    
    def get_all_conversations(self) -> pd.DataFrame:
        """Retrieve all conversations as DataFrame"""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM conversations ORDER BY conversation_date DESC", conn)
        conn.close()
        return df
    
    def get_conversation_by_id(self, conv_id: int) -> Optional[Dict]:
        """Get a single conversation by database ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def get_conversation_by_source_id(self, source_id: str) -> Optional[Dict]:
        """Get a conversation by source_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversations WHERE source_id = ?", (source_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def insert_conversation(self, record: Dict[str, Any]) -> int:
        """Insert a new conversation record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        record['created_at'] = now
        record['updated_at'] = now
        record['record_hash'] = self.calculate_record_hash(record)
        
        columns = list(record.keys())
        placeholders = ','.join(['?' for _ in columns])
        column_names = ','.join(columns)
        
        query = f"INSERT INTO conversations ({column_names}) VALUES ({placeholders})"
        cursor.execute(query, [record[col] for col in columns])
        
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        
        return record_id
    
    def update_conversation(self, source_id: str, updates: Dict[str, Any], 
                          preserve_manual: bool = True) -> bool:
        """Update an existing conversation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get current record
        existing = self.get_conversation_by_source_id(source_id)
        if not existing:
            conn.close()
            return False
        
        # Preserve manually overridden fields
        if preserve_manual and existing.get('manual_override') == 'TRUE':
            manual_fields = json.loads(existing.get('manual_override_fields', '[]'))
            for field in manual_fields:
                if field in updates:
                    del updates[field]
        
        updates['updated_at'] = datetime.now().isoformat()
        
        # Recalculate hash if content fields changed
        merged = {**existing, **updates}
        updates['record_hash'] = self.calculate_record_hash(merged)
        
        set_clause = ','.join([f"{k} = ?" for k in updates.keys()])
        query = f"UPDATE conversations SET {set_clause} WHERE source_id = ?"
        
        cursor.execute(query, list(updates.values()) + [source_id])
        conn.commit()
        conn.close()
        
        return True
    
    def log_audit_event(self, action_type: str, record_id: Optional[str] = None,
                       field_name: Optional[str] = None, previous_value: Optional[str] = None,
                       new_value: Optional[str] = None, reason: Optional[str] = None,
                       metadata: Optional[Dict] = None):
        """Log an audit event"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_log 
            (timestamp, action_type, record_id, field_name, previous_value, new_value, reason, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            action_type,
            record_id,
            field_name,
            previous_value,
            new_value,
            reason,
            json.dumps(metadata) if metadata else None
        ))
        
        conn.commit()
        conn.close()
    
    def get_audit_log(self, limit: int = 100) -> pd.DataFrame:
        """Retrieve audit log"""
        conn = self.get_connection()
        df = pd.read_sql_query(
            "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?", 
            conn, 
            params=(limit,)
        )
        conn.close()
        return df
    
    def log_import(self, filename: str, stats: Dict[str, int], status: str, details: str = ""):
        """Log an import operation"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO import_history 
            (timestamp, filename, total_records, new_records, updated_records, 
             unchanged_records, duplicate_records, failed_records, status, details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            filename,
            stats.get('total', 0),
            stats.get('new', 0),
            stats.get('updated', 0),
            stats.get('unchanged', 0),
            stats.get('duplicates', 0),
            stats.get('failed', 0),
            status,
            details
        ))
        
        conn.commit()
        conn.close()
    
    def get_import_history(self) -> pd.DataFrame:
        """Retrieve import history"""
        conn = self.get_connection()
        df = pd.read_sql_query(
            "SELECT * FROM import_history ORDER BY timestamp DESC", 
            conn
        )
        conn.close()
        return df
