


sudo apt update
sudo apt install nginx
sudo apt install redis
sudo systemctl restart redis-server


sudo cp setup/daphne.socket /etc/systemd/system/daphne.socket
sudo cp setup/daphne.service /etc/systemd/system/daphne.service

sudo systemctl start daphne.socket
sudo systemctl enable daphne.socket

sudo systemctl daemon-reload
sudo systemctl restart daphne

sudo cp setup/adv_tv_nginx /etc/nginx/sites-available/kehilaton_nginx.conf
sudo ln -s /etc/nginx/sites-available/kehilaton_nginx.conf /etc/nginx/sites-enabled

sudo nginx -t
sudo systemctl restart nginx

sudo apt install libpq-dev python3-dev
sudo apt install python3.8-venv
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
