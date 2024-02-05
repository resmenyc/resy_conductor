source .venv/bin/activate
git fetch
git pull origin main
pip3 install -r requirements
pm2 restart resme_accs_check_working
pm2 restart resme_accs_recycle
