"""
Quick script to load sample data into SignalDesk database
"""
from src.database import Database
from src.ingestion import process_import
from pathlib import Path

# Initialize database
db = Database()

# Load sample data
sample_path = "data/sample_conversations.csv"

if Path(sample_path).exists():
    print("Loading sample data...")
    result = process_import(sample_path, db)
    
    if result['success']:
        print(f"\n✅ Successfully loaded sample data!")
        print(f"   Total records: {result['stats']['total']}")
        print(f"   New records: {result['stats']['new']}")
        print(f"   Updated records: {result['stats']['updated']}")
        print(f"   Unchanged records: {result['stats']['unchanged']}")
        
        if result['stats'].get('failed', 0) > 0:
            print(f"   ⚠️ Failed records: {result['stats']['failed']}")
    else:
        print(f"\n❌ Error loading data: {result.get('error')}")
else:
    print(f"❌ Sample data file not found at: {sample_path}")

print("\n🎉 You can now refresh your browser and explore the data!")
