# SignalDesk AI — Quick Start Guide

**Get the app running in 5 minutes!**

---

## ✅ Prerequisites Check

Before you start, verify:
- [ ] Windows OS
- [ ] Python 3.11 or higher installed
- [ ] PowerShell or Command Prompt available
- [ ] Internet connection (for downloading dependencies)

Check Python version:
```powershell
python --version
```
Expected output: `Python 3.11.x` or higher

---

## 🚀 Installation Steps

### Step 1: Navigate to Project Directory
```powershell
cd C:\Users\ajith\Downloads\Yolopay
```
*(Replace with your actual project path)*

### Step 2: Create Virtual Environment
```powershell
python -m venv .venv
```

### Step 3: Activate Virtual Environment

**Option A: PowerShell**
```powershell
.\.venv\Scripts\Activate.ps1
```

**If blocked**, run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activation again.

**Option B: Command Prompt**
```cmd
.venv\Scripts\activate.bat
```

You should see `(.venv)` at the start of your command prompt.

### Step 4: Upgrade pip
```powershell
python -m pip install --upgrade pip
```

### Step 5: Install Dependencies
```powershell
pip install -r requirements.txt
```

This will install:
- streamlit
- pandas
- plotly
- openpyxl
- pytest
- python-dotenv

**Wait time**: 1-2 minutes

### Step 6: Verify Installation
```powershell
python manual_test.py
```

**Expected output**:
```
============================================================
✓ ALL TESTS PASSED
============================================================
```

If you see this, you're ready to go! 🎉

### Step 7: Launch Application
```powershell
python -m streamlit run app.py
```

**Expected output**:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

Your browser should automatically open to `http://localhost:8501`

---

## 📊 First Time Setup

### Load Demo Data

1. **Navigate to Import Page**
   - Click **"📥 Import & Sync"** in the sidebar

2. **Load Sample Dataset**
   - Click the **"📊 Load Sample Dataset"** button
   - Wait for success message
   - You should see: "12 new records imported"

3. **Explore the Dashboard**
   - Click **"📈 Executive Dashboard"** in sidebar
   - You should see metrics, charts, and data

---

## 🧪 Quick Verification Tests

### Test 1: Dashboard Works
- [ ] Navigate to **📈 Executive Dashboard**
- [ ] See "12" total conversations
- [ ] Charts render without errors
- [ ] Filters work (try changing stage)

### Test 2: Routing Works
- [ ] Navigate to **🎯 Intelligent Routing Lab**
- [ ] Select any conversation
- [ ] Click **"🎯 Calculate Routing"**
- [ ] See recommended team and priority score

### Test 3: Findings Work
- [ ] Navigate to **🔍 Findings & Decisions**
- [ ] See 3+ findings displayed
- [ ] Each finding shows evidence quotes
- [ ] Supporting conversation IDs present

### Test 4: Export Works
- [ ] Navigate to **📤 Export Center**
- [ ] Click **"📥 Export All Conversations"**
- [ ] Download button appears
- [ ] CSV file downloads successfully

### Test 5: Duplicate Prevention Works
- [ ] Go to **📥 Import & Sync**
- [ ] Click **"📊 Load Sample Dataset"** again
- [ ] Should show "12 unchanged, 0 new"
- [ ] No duplicates created

---

## 🛑 Troubleshooting

### Problem: "Streamlit is not recognized"
**Cause**: Virtual environment not activated  
**Solution**: Go back to Step 3 and activate virtual environment

### Problem: "No module named 'streamlit'"
**Cause**: Dependencies not installed  
**Solution**: Run `pip install -r requirements.txt` again

### Problem: "Port 8501 is already in use"
**Cause**: Another Streamlit app is running  
**Solution**: 
- Stop other Streamlit apps
- Or run on different port: `streamlit run app.py --server.port 8502`

### Problem: "Cannot load sample dataset"
**Cause**: File path issue  
**Solution**: Verify file exists at `data/sample_conversations.csv`

### Problem: Charts not displaying
**Cause**: Browser compatibility  
**Solution**: Try Chrome or Edge browser

---

## 📖 What to Do Next

### Learn the Features (15 minutes)
1. **Dashboard** — View metrics and pipeline
2. **Explorer** — Search and filter conversations
3. **Routing Lab** — Test intelligent routing
4. **Findings** — Review insights
5. **Import** — Try importing a file
6. **Editing** — Manually change a conversation
7. **Export** — Download your data

### Run Full Tests (5 minutes)
```powershell
pytest tests/ -v
```

### Try Your Own Data (30 minutes)
1. Download CSV template from Import page
2. Add your conversation data
3. Upload and import
4. See routing recommendations for your data

### Create Presentation (45 minutes)
- Open `slides/SignalDesk_Presentation_Content.md`
- Create PowerPoint using that content
- Add charts and diagrams

### Record Demo (20 minutes)
- Follow script in `recording/narration_script.md`
- Use screen recorder
- Target 3 minutes

### Deploy to Cloud (Optional, 30 minutes)
- Follow `DEPLOYMENT_CHECKLIST.md`
- Push to GitHub
- Deploy on Streamlit Cloud

---

## ⚡ Super Quick Start (1 command)

If you have `make` installed:
```powershell
# Coming soon
```

For now, use the manual steps above.

---

## 📞 Need Help?

1. Check `README.md` for detailed documentation
2. Check `PROJECT_SUMMARY.md` for project overview
3. Check `DEPLOYMENT_CHECKLIST.md` for deployment help
4. Review error messages carefully — they contain helpful info

---

## ✅ Success Checklist

You're ready when:
- [x] Virtual environment activated (see `(.venv)` in prompt)
- [x] Dependencies installed (no errors)
- [x] Manual test passes (✓ ALL TESTS PASSED)
- [x] App launches (browser opens to localhost:8501)
- [x] Sample data loads (12 conversations imported)
- [x] Dashboard shows metrics and charts
- [x] All pages accessible from sidebar

---

**🎉 Congratulations! SignalDesk AI is ready to use!**

Explore the features, test the routing engine, and see how intelligent sales conversation management works.

---

**Questions?** Review the comprehensive `README.md` file for detailed information about each feature.
