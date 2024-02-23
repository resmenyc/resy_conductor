curl 'https://api.ipify.org?format=json'
echo
mullvad relay set location us
mullvad reconnect
curl 'https://api.ipify.org?format=json'