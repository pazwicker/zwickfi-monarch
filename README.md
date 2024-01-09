# zwickfi-monarch
Zwickfi for Monarch Money

# Deployment
1. Deployed to Cloud Run in Google Cloud Platform
2. Configured to build in Google Cloud Build on merge to `main` branch
3. Google Cloud Scheduler scheduled to call container every hour at minute zero
4. Flask app configured to run `zwickfi.py` when called from Cloud Scheduler
