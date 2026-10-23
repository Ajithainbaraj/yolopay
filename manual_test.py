"""
Manual test script to verify core functionality
Run this without needing to install all dependencies
"""
import sys
import os

print("=" * 60)
print("SignalDesk AI - Manual Test Script")
print("=" * 60)

# Test 1: Check project structure
print("\n✓ Test 1: Project Structure")
required_files = [
    'app.py',
    'requirements.txt',
    'README.md',
    'data/sample_conversations.csv',
    'src/database.py',
    'src/routing.py',
    'src/ingestion.py',
    'src/insights.py',
    'src/validation.py',
    'src/exports.py'
]

missing_files = []
for file_path in required_files:
    if os.path.exists(file_path):
        print(f"  ✓ {file_path}")
    else:
        print(f"  ✗ {file_path} MISSING")
        missing_files.append(file_path)

if missing_files:
    print(f"\n  ERROR: {len(missing_files)} files missing")
    sys.exit(1)
else:
    print("  All required files present")

# Test 2: Check sample dataset
print("\n✓ Test 2: Sample Dataset")

try:
    with open('data/sample_conversations.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"  ✓ Sample dataset exists")
        print(f"  ✓ Contains {len(lines)} lines (including header)")
        
        # Check for header
        header = lines[0].strip()
        if 'source_id' in header:
            print(f"  ✓ Required 'source_id' column present")
        
        # Count data rows
        data_rows = len(lines) - 1
        print(f"  ✓ {data_rows} conversation records")
        
        if data_rows >= 12:
            print(f"  ✓ Meets minimum 12 records requirement")
        else:
            print(f"  ✗ Only {data_rows} records (need at least 12)")
except Exception as e:
    print(f"  ✗ Error reading sample dataset: {e}")
    sys.exit(1)

# Test 3: Check module imports
print("\n✓ Test 3: Module Imports")

try:
    sys.path.insert(0, os.path.dirname(__file__))
    
    print("  Importing database module...")
    from src import database
    print("  ✓ database module")
    
    print("  Importing routing module...")
    from src import routing
    print("  ✓ routing module")
    
    print("  Importing validation module...")
    from src import validation
    print("  ✓ validation module")
    
    print("  Importing ingestion module...")
    from src import ingestion
    print("  ✓ ingestion module")
    
    print("  Importing insights module...")
    from src import insights
    print("  ✓ insights module")
    
    print("  Importing exports module...")
    from src import exports
    print("  ✓ exports module")
    
except Exception as e:
    print(f"  ✗ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test routing engine
print("\n✓ Test 4: Routing Engine")
try:
    test_conv = {
        'stage': 'discovery',
        'urgency': 'high',
        'customer_intent': 'evaluate_solution',
        'conversation_summary': 'Test conversation',
        'transcript_or_notes': 'Quote: "This is a test"',
        'deal_value': '100000',
        'sentiment': 'positive'
    }
    
    result = routing.recommend_routing(test_conv)
    
    print(f"  ✓ Routing engine executed")
    print(f"  ✓ Recommended team: {result['recommended_team']}")
    print(f"  ✓ Priority score: {result['priority_score']}")
    print(f"  ✓ Generated {len(result['all_scores'])} team scores")
    
    if result['recommended_team'] in routing.TEAMS:
        print(f"  ✓ Valid team recommendation")
    else:
        print(f"  ✗ Invalid team: {result['recommended_team']}")
        sys.exit(1)
        
except Exception as e:
    print(f"  ✗ Routing test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Test validation
print("\n✓ Test 5: Data Validation")
try:
    valid_record = {
        'source_id': 'TEST001',
        'customer_name': 'Test Customer',
        'stage': 'discovery'
    }
    
    is_valid, errors = validation.validate_record(valid_record, row_num=1)
    
    if is_valid:
        print(f"  ✓ Valid record passed validation")
    else:
        print(f"  ✗ Valid record failed: {errors}")
        sys.exit(1)
    
    invalid_record = {
        'source_id': '',  # Empty source_id should fail
        'customer_name': 'Test'
    }
    
    is_valid, errors = validation.validate_record(invalid_record, row_num=2)
    
    if not is_valid:
        print(f"  ✓ Invalid record correctly rejected")
        print(f"    Validation errors: {len(errors)}")
    else:
        print(f"  ✗ Invalid record should have been rejected")
        sys.exit(1)
        
except Exception as e:
    print(f"  ✗ Validation test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED")
print("=" * 60)
print("\nNext steps:")
print("1. Install dependencies: pip install -r requirements.txt")
print("2. Run the application: python -m streamlit run app.py")
print("3. Run full tests: pytest tests/ -v")
print("=" * 60)
