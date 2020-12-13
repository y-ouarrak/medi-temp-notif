import sys

import pika
import http.client
from utils.env import *
import json
import os
import urllib.parse
import requests
import time
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


data = '''Bonjour,
L’enregistreur installé au niveau de la localisation https://www.google.com/maps/search/?api=1&query={1},{2} affiche l’alerte 
{3}.
Nextronic
0520603030'''
alert = {
    "1": "Température élevée",
    "2": "Température trop basse",
    "3": "Enregistreur déconnecté",
    "4": "Enregistreur connecté",
    "5": "Température rétablie",
    "6": "Température en tendance haussière",
}


credentials = pika.PlainCredentials(rabbit_user, rabbit_passwd)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=rabbit_host, credentials=credentials))
channel = connection.channel()
channel.queue_declare(queue=alert_queue, durable=True)


def send_alert(ch, method, properties, body):
    try:
        tmp = json.loads(body.decode('utf8'))
        print(tmp)
        send_sms(tmp["phones"], alert[str(tmp["type"])],
                 str(tmp["lat"]), str(tmp["lng"]))
        send_email(tmp["emails"], alert[str(tmp["type"])],
                   tmp["name"], str(tmp["lat"]), str(tmp["lng"]))
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as ex:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(ex)
        return


def send_sms(to, alert, lat, lng):
    try:
        for item in to:
            pload = {'Password': sms_passwd, 'Text':
                     data.replace('{1}', lat).replace('{2}', lng).replace('{3}', alert), 'User': sms_user, 'Phone': item}
            r = requests.post(sms_url, data=pload)
            print(r)
            time.sleep(0.5)
    except Exception as ex:
        print(ex)
        return


def send_email(to, alert, device, lat, lng):
    msg = "Bonjour,\n\nCe mail est pour vous informer que l'enregistreur N° {} installé au niveau de la localisation ci-dessous : \nhttps://www.google.com/maps/search/?api=1&query={},{} \n\nAffiche le message d'alerte suivant : {}\nNous vous prions de vous assurer des conditions de température de l'équipement de stockage.\n\nSachez que notre service après vente reste à votre entière disposition au 05 20 60 30 30 du lundi au Dimanche de 8h à 20h. \n\nCordiales salutations,\n\nService Après Vente NEXTRONIC\n0520603030"
    try:
        for item in to:
            _msg = MIMEMultipart()  # create a message
            _msg.attach(
                MIMEText(msg.format(device, lat, lng, alert), 'plain'))
            _msg['Subject'] = f"Alert l'enregistreur {device}"
            _msg['From'] = mail_user
            _msg['To'] = item
            mailserver = smtplib.SMTP(smtp_host, smtp_port)
            mailserver.ehlo()
            mailserver.starttls()
            mailserver.login(mail_user, mail_passwd)
            mailserver.send_message(_msg)
            mailserver.quit()
            time.sleep(2)
    except Exception as ex:
        print(ex)
        return


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=alert_queue, on_message_callback=send_alert)
channel.start_consuming()
