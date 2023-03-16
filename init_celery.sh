
sudo cp ./setup/adv_control_celery.conf /etc/supervisor/conf.d/adv_control_celery.conf
sudo cp ./setup/adv_control_celerybeat.conf /etc/supervisor/conf.d/adv_control_celerybeat.conf
sudo mkdir -p /var/log/celery
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart advcontrolcelery
sudo supervisorctl restart advcontrolcelerybeat