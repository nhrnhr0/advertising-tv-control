
from server.settings.secrects import BASE_MY_DOMAIN
from .celery import app as celery_app
from django.utils import timezone
from datetime import timedelta
from server.telegram_bot_interface import send_admin_message,edit_message_reply_markup
import logging
@celery_app.task
def monitor_pi_devices():
    # ALERT_THRESHOLD = 15 minutes
    # create a random file on disk  
    with open('monitor_pi_devices.txt', 'w') as f:
        f.write('monitor_pi_devices')
    
    send_admin_message('monitor_pi_devices')
    ALERT_THRESHOLD = 60 * 15
    # print('='*20,'monitor_pi_devices','='*20)
    from pi.models import PiDevice
    qs = PiDevice.objects.filter(is_approved=True)
    logging.info('monitor_pi_devices %s', qs.count())
    for pi_device in qs:
        if pi_device.socket_status_updated:
            # print('compare', pi_device.socket_status_updated, timezone.now() - timedelta(seconds=ALERT_THRESHOLD))
            if (pi_device.socket_status_updated < timezone.now() - timedelta(seconds=ALERT_THRESHOLD)) and not pi_device.telegram_connection_error_sent:
                
                # send alert
                href = BASE_MY_DOMAIN
                try:
                    if pi_device.tv:
                        # print('send alert to admin', pi_device)
                        logging.info('send alert to admin %s', pi_device)
                        href += pi_device.tv.get_dashboard_url()
                        str_time = pi_device.socket_status_updated.strftime("%m/%d/%Y, %H:%M:%S")
                        send_admin_message(f'🛑🛑🛑לא קיבלתי שום תקשורת מהמכשיר <b><a href="{href}">{pi_device.name}</a></b> ברבע שעה האחרונה\nעדכון אחרון שקיבלתי: <b>{str_time}</b>')
                        
                        logging.info('send alert to admin %s', pi_device)
                        pi_device.telegram_connection_error_sent = True
                        pi_device.save()
                        pass
                except:
                    pass
                
    # 
# device_id
# name
# remote_last_image
# image_updated
# socket_status_updated
# cec_hdmi_status
# is_approved