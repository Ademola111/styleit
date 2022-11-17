from flask_mail import Message
from styleitapp import app, mail
from styleitapp.models import Designer, Customer
def send_email(to, subject, template):
    
    msg = Message(
        subject, 
        recipients=[to], 
        html=template, 
        sender=app.config['MAIL_DEFAULT_SENDER'],
        # sender='admin@styleit.com'
        )
    mail.send(msg)