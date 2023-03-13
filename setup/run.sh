


sudo apt update
sudo apt install nginx

sudo cp setup/daphne.socket /etc/systemd/system/daphne.socket
sudo cp setup/daphne.service /etc/systemd/system/daphne.service

sudo systemctl start daphne.socket
sudo systemctl enable daphne.socket

sudo systemctl daemon-reload
sudo systemctl restart daphne

sudo cp setup/nginx.conf /etc/nginx/sites-available/kehilaton_nginx.conf
sudo ln -s /etc/nginx/sites-available/kehilaton_nginx.conf /etc/nginx/sites-enabled

sudo nginx -t
sudo systemctl restart nginx

