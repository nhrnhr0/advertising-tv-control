git pull
source env/bin/activate
pip install -r requirements.txt
python server/manage.py migrate 
sudo supervisorctl restart gunicornGoldTV
sudo service nginx restart
