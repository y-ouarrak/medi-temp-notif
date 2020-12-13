from dotenv import load_dotenv
from os import environ
load_dotenv()

rabbit_user = environ.get('RABBIT_USER')
rabbit_passwd = environ.get('RABBIT_PASSWD')
rabbit_host = environ.get('RABBIT_HOST')
alert_queue = environ.get('ALERT_QUEUE')
sms_url = environ.get('SMS_URL')
sms_user = environ.get('SMS_USER')
sms_passwd = environ.get('SMS_PASSWD')
smtp_host = environ.get('SMTP_HOST')
smtp_port = environ.get('SMTP_PORT')
mail_user = environ.get('MAIL_USER')
mail_passwd = environ.get('MAIL_PASSWD')
