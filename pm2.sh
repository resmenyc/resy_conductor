source .venv/bin/activate
pip3 install -r requirements
pm2 start ./check_working.py --name "resme_accs_check_working" -i 1
pm2 start ./recycle.py --name "resme_accs_recycle" -i 1
