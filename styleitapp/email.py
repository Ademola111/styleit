from flask_mail import Message
from styleitapp import app, mail
from styleitapp.models import Designer, Customer

"""email alert for activation of account"""
def send_email(to, subject, template):
    
    msg = Message(
        subject, 
        recipients=[to], 
        html=template, 
        sender=app.config['MAIL_DEFAULT_SENDER'],
        # sender='admin@styleit.com'
        )
    mail.send(msg)

"""email alert for every action on the web"""
def send_email_alert(subject, body, recipients):
    msg = Message(subject, recipients=recipients)
    msg.body = body
    mail.send(msg)