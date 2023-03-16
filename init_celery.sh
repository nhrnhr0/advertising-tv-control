
sudo cp ./setup/adv_control_celery.conf /etc/supervisor/conf.d/adv_control_celery.conf
sudo cp ./setup/adv_control_celerybeat.conf /etc/supervisor/conf.d/adv_control_celerybeat.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart adv_control_celery
sudo supervisorctl restart adv_control_celerybeatc