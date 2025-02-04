import smtplib
import os
from dotenv import load_dotenv
from os.path import join, dirname

ruta_archivo_env = join(dirname(__file__), 'cred.env')
load_dotenv(ruta_archivo_env)

def notificaciones(correos):
    gmail_user = os.getenv('GMAIL_USER')
    app_password = os.getenv('APP_PASSWORD')
    sent_from = gmail_user
    to = correos
    subject = 'Notificación de evento'
    body = 'Alerta de evento próximo, eres asistente a un evento para más información mira en el aplicativo'

    mensaje = f"Subject: {subject}\n\n{body}"

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, app_password)
        smtp_server.sendmail(sent_from, to, mensaje.encode('utf-8'))
        smtp_server.close()
        print ("Notificaciones enviadas")
    except Exception as err:
        print ("Error en el envio", err)
    return "OK"