git pull
source env/bin/activate
pip install -r requirements.txt
python server/manage.py migrate 
env/bin/python server/manage.py collectstatic --noinput
sudo systemctl daemon-reload
sudo systemctl restart daphne
sudo service nginx restart
echo 'done'
