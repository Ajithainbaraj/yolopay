# SignalDesk AI — Sales Intelligence Inbox

**Intelligent sales conversation analysis, routing, and decision support platform**

![Demo Mode](https://img.shields.io/badge/Demo-Synthetic%20Data-yellow)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red)

## 🎯 Overview

SignalDesk AI is a sales intelligence platform that helps sales managers analyze conversations, identify opportunities, route leads intelligently, and make data-driven decisions. Built with explainability and human oversight at its core.

## 🚀 Problem Statement

Sales teams struggle with:
- **Scattered conversation data** across multiple systems
- **Missed opportunities** due to lack of visibility
- **Inefficient routing** causing delays and misalignment
- **Duplicate records** when reimporting data
- **Lost context** when manual corrections are overwritten

## ✨ Unique Solution

SignalDesk AI provides:

1. **Explainable Routing**: Transparent team recommendations with scoring and reasoning
2. **Evidence-Backed Insights**: Every finding linked to actual conversation quotes
3. **Duplicate-Aware Sync**: Reimporting files doesn't create duplicates
4. **Human-in-the-Loop**: Manual corrections preserved across imports
5. **Change Detection**: Identifies new, updated, unchanged, and duplicate records
6. **Audit Trail**: Complete history of all data changes and decisions

## 🛠️ Technology Stack

- **Language**: Python 3.11+
- **Web Framework**: Streamlit
- **Data Processing**: Pandas
- **Database**: SQLite
- **Visualizations**: Plotly
- **Testing**: pytest

## 📁 Project Structure

```
SignalDesk_AI/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
├── .env.example                    # Environment configuration template
├── data/
│   └── sample_conversations.csv    # Demo dataset (SYNTHETIC DATA)
├── src/
│   ├── database.py                 # Database management
│   ├── ingestion.py                # CSV/Excel import with sync
│   ├── routing.py                  # Intelligent routing engine
│   ├── insights.py                 # Findings generator
│   ├── validation.py               # Data validation
│   └── exports.py                  # Export with checksums
├── tests/
│   ├── test_database.py
│   ├── test_ingestion.py
│   ├── test_routing.py
│   └── test_exports.py
├── exports/                        # Generated exports
├── slides/
│   └── SignalDesk_Findings.pptx   # Presentation (to be created)
└── recording/
    └── narration_script.md         # Recording guide
```

## 🚀 Installation & Setup (Windows)

### Prerequisites
- Python 3.11 or higher
- PowerShell (pre-installed on Windows)

### Step-by-Step Installation

1. **Clone or download this project**
```powershell
cd path\to\SignalDesk_AI
```

2. **Create virtual environment**
```powershell
python -m venv .venv
```

3. **Activate virtual environment**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Note**: If PowerShell blocks script execution, you have two options:

**Option A** (Recommended): Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Option B**: Use Command Prompt instead:
```cmd
.venv\Scripts\activate.bat
```

4. **Upgrade pip**
```powershell
python -m pip install --upgrade pip
```

5. **Install dependencies**
```powershell
pip install -r requirements.txt
```

6. **Run the application**
```powershell
python -m streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## 📊 Using the Application

### Quick Start

1. **Load Sample Data**
   - Navigate to **📥 Import & Sync**
   - Click **"📊 Load Sample Dataset"**
   - Wait for confirmation

2. **Explore the Dashboard**
   - Go to **📈 Executive Dashboard**
   - Review metrics, charts, and pipeline value

3. **Test Routing**
   - Open **🎯 Intelligent Routing Lab**
   - Select a conversation
   - Click **"🎯 Calculate Routing"**
   - Review recommendations and scores

4. **View Findings**
   - Navigate to **🔍 Findings & Decisions**
   - Review evidence-backed insights

5. **Export Data**
   - Go to **📤 Export Center**
   - Generate exports with manifest

### Importing Your Own Data

1. Download the CSV template from **📥 Import & Sync** → **Sample Template**
2. Fill in your conversation data (minimum: `source_id` column required)
3. Upload the CSV file
4. Review the preview
5. Confirm import

**Important**: 
- `source_id` must be unique for each conversation
- Reimporting the same file will not create duplicates
- Changed records will update automatically
- Manual corrections are preserved unless explicitly reset

## 🧪 Testing

Run automated tests:

```powershell
pytest tests/ -v
```

Run specific test file:

```powershell
pytest tests/test_ingestion.py -v
```

### Manual Acceptance Tests

**Test 1: Duplicate Import Prevention**

1. Load the sample dataset
2. Note the record count
3. Import `data/sample_conversations.csv` again
4. Verify "Unchanged" count equals total records
5. Verify "New" count is 0
6. Check database has no duplicate records

**Test 2: Manual Correction Persistence**

1. Load the sample dataset
2. Go to **🎯 Routing Lab** → Select CONV001
3. Calculate routing and note the recommended team
4. Go to **✏️ Manual Editing**
5. Change the owner to a different team
6. Save changes
7. Go back to **📥 Import & Sync**
8. Reimport `data/sample_conversations.csv`
9. Go to **💬 Conversation Explorer**
10. View CONV001 details
11. Verify the owner is still your manually selected team (not reverted)

## 📦 Deployment

### Streamlit Community Cloud

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/signaldesk-ai.git
git push -u origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file: `app.py`
   - Click "Deploy"

3. **Note**: SQLite database will be ephemeral on Streamlit Cloud. For production, consider PostgreSQL or external storage.

## 🎨 Features

### Executive Dashboard
- Real-time metrics and KPIs
- Pipeline value calculation
- Interactive charts (stage, owner, priority, sentiment)
- Recent activity tracking
- Configurable filters

### Conversation Explorer
- Search across all fields
- Filter by stage, sentiment, owner
- Detailed conversation view
- Evidence quote display

### Intelligent Routing Lab
- Transparent routing recommendations
- All team scores displayed
- Evidence-backed reasoning
- Manual override capability
- Difficult routing example walkthrough

### Findings & Decision Support
- Evidence-backed insights
- Supporting conversation IDs
- Actual source quotes
- Limitations disclosure
- Rejected decision analysis

### Import & Synchronization
- CSV and Excel support
- Duplicate detection within files
- Change tracking (new/updated/unchanged)
- Validation with helpful errors
- Import history
- Template download

### Manual Editing & Audit
- Edit conversations with validation
- Reset manual overrides
- Complete audit log
- Change tracking
- Filter audit events

### Export Center
- Conversations CSV
- Routing decisions CSV
- Findings JSON
- Audit log export
- Manifest with SHA-256 checksums

## ⚠️ Important Notes

### Synthetic Demo Data

**All sample data is synthetic and fictional.** The demo dataset includes 12 synthetic conversations created for demonstration purposes. No real customer data, business metrics, or actual conversations are included.


### Privacy & Security

- All data stored locally in SQLite database
- No external API calls by default
- No sensitive data sent to third parties
- Suitable for confidential sales data

### Limitations

- **Small sample size**: Demo includes only 12 conversations
- **Local database**: SQLite not suitable for high-concurrency production use
- **No authentication**: Add auth layer for multi-user deployment
- **Ephemeral on Streamlit Cloud**: Database resets on app restart
- **Rules-based routing**: No ML model training (design choice for explainability)
- **Manual sentiment tagging**: No automatic sentiment analysis (privacy/cost trade-off)

## 🔮 Future Enhancements

- PostgreSQL support for production
- User authentication and role-based access
- Email notifications for high-priority conversations
- Slack/Teams integration
- Custom routing rules editor
- Bulk edit capabilities
- Advanced analytics dashboard
- Optional LLM integration for enhanced analysis

## 📄 License

This project is for educational and demonstration purposes.

## 🤝 Support

For issues or questions:
1. Check the manual acceptance test guide
2. Review validation error messages
3. Check audit log for change history

## 📊 Metrics Calculation Notes

- **Pipeline Value**: Sum of known deal values in discovery, proposal, and negotiation stages
- **Priority Score**: Calculated from urgency, stage, deal value, and sentiment (0-100)
- **High Priority**: Conversations with priority score ≥ 75
- **Follow-ups Due**: Follow-up dates within next 7 days

---

**Built with ❤️ for sales teams | Demo Mode: Synthetic Data Only**
