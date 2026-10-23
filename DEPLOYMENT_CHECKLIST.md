# SignalDesk AI Deployment Checklist

## Pre-Deployment

- [ ] All automated tests pass (`pytest tests/ -v`)
- [ ] Manual acceptance tests completed
- [ ] Sample dataset loads successfully
- [ ] All pages render without errors
- [ ] Exports generate correctly with valid checksums
- [ ] README installation instructions verified on Windows
- [ ] .gitignore excludes sensitive files (.env, *.db)
- [ ] requirements.txt includes all dependencies with versions

## GitHub Repository Setup

- [ ] Create new GitHub repository
- [ ] Initialize git in project directory
- [ ] Add all files to git
- [ ] Create initial commit
- [ ] Push to GitHub main branch
- [ ] Verify all files uploaded correctly
- [ ] Check that .gitignore is working (no .db or .env files uploaded)

## Streamlit Cloud Deployment

- [ ] Sign in to [share.streamlit.io](https://share.streamlit.io)
- [ ] Click "New app"
- [ ] Select GitHub repository
- [ ] Set main file path: `app.py`
- [ ] Configure Python version: 3.11
- [ ] (Optional) Add secrets if using external APIs
- [ ] Click "Deploy"
- [ ] Wait for deployment to complete
- [ ] Test deployed URL

## Post-Deployment Verification

- [ ] Visit the deployed app URL
- [ ] Load sample dataset successfully
- [ ] Navigate to all pages without errors
- [ ] Test routing recommendation
- [ ] View findings page
- [ ] Test export functionality
- [ ] Verify imports work correctly
- [ ] Check that duplicate import prevention works
- [ ] Test manual editing
- [ ] Review audit log

## Known Limitations on Streamlit Cloud

⚠️ **Important**: Streamlit Community Cloud uses ephemeral file storage

- Database file (`signaldesk.db`) will reset when the app restarts
- Uploaded files are not persisted across sessions
- For production use, consider:
  - PostgreSQL database with connection pooling
  - External file storage (S3, Google Cloud Storage)
  - Dedicated hosting with persistent storage

## Database Persistence Options

### Option 1: PostgreSQL (Recommended for Production)
- Create PostgreSQL database (e.g., on Supabase, Railway, or AWS RDS)
- Update `src/database.py` to use PostgreSQL connection
- Add database URL to Streamlit secrets
- Test connection pooling for concurrent users

### Option 2: SQLite with Volume Mount
- Deploy on platform with persistent volumes (e.g., AWS EC2, DigitalOcean)
- Mount volume for database directory
- Configure backup schedule

### Option 3: Accept Ephemeral Storage
- Document that demo resets on restart
- Provide sample data reload option
- Suitable for demos and testing only

## Security Checklist

- [ ] No API keys or secrets in code
- [ ] Sensitive configuration in .env (not committed)
- [ ] .gitignore properly configured
- [ ] HTTPS enabled (automatic on Streamlit Cloud)
- [ ] Consider adding authentication for production
- [ ] Review data privacy implications
- [ ] Ensure compliance with data regulations

## Monitoring

- [ ] Check Streamlit Cloud logs for errors
- [ ] Monitor app performance metrics
- [ ] Set up uptime monitoring (optional)
- [ ] Test app after Streamlit platform updates

## Maintenance

- [ ] Document deployment date and version
- [ ] Keep requirements.txt updated
- [ ] Test on Python version updates
- [ ] Review and update security dependencies
- [ ] Backup database if using persistent storage

## Rollback Plan

If deployment fails:
1. Check Streamlit Cloud logs for specific errors
2. Verify requirements.txt dependencies are compatible
3. Test locally to reproduce the issue
4. Fix issue and redeploy
5. If necessary, revert to previous GitHub commit

## Support Resources

- Streamlit Documentation: https://docs.streamlit.io
- Streamlit Community Forum: https://discuss.streamlit.io
- GitHub Issues: (your repository URL)

---

**Deployment Date**: ___________  
**Deployed By**: ___________  
**Deployed URL**: ___________  
**Status**: ___________
