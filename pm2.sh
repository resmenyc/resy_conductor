pm2 start ./check_working.py --name "resme_conductor_check_working" -i 1 --interpreter=.venv/bin/python3
pm2 start ./recycle.py --name "resme_conductor_recycle" -i 1 --interpreter=.venv/bin/python3
pm2 start ./discord_bot.py --name "resme_conductor_discord" -i 1 --interpreter=.venv/bin/python3