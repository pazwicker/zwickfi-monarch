# zwickfi-monarch
Zwickfi for Monarch Money

# Deployment
1. Deployed to Cloud Run in Google Cloud Platform
2. Configured to build in Google Cloud Build on merge to `main` branch
3. Google Cloud Scheduler scheduled to call container every hour at minute zero
4. GO server configured to run `invoke.go` when called from Cloud Scheduler
5. `invoke.go` includes a command to run `dev_script.sh`
6. `dev_script.sh` calls `zwickfi.py`