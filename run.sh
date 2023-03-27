


sudo apt update
sudo apt install nginx
sudo apt install redis
sudo apt install supervisor
sudo systemctl restart redis-server
 

sudo cp setup/daphne_workers.conf /etc/supervisor/conf.d/daphne_workers.conf
sudo mkdir /var/log/gunicorn
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart daphne_workers

sudo cp setup/adv_tv_nginx /etc/nginx/sites-available/kehilaton_nginx.conf
sudo ln -s /etc/nginx/sites-available/kehilaton_nginx.conf /etc/nginx/sites-enabled

sudo nginx -t
sudo systemctl restart nginx

sudo apt install libpq-dev python3-dev
sudo apt install python3.8-venv
sudo apt install python3-virtualenv -y
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
