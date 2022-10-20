
import smtplib
import smtplib, ssl
from email.message import EmailMessage

#Hier noch passwort setzen
#https://betterdatascience.com/send-emails-with-python/
EMAIL_PASSWORD = ""

msg = EmailMessage()
msg['Subject'] = 'This is my first Python email'
msg['From'] = "mcrc-db@charite.de" 
msg['To'] = "hannes.freitag@charite.de" 
msg.set_content('And it actually works')

port = 587  # For starttls
smtp_server = "email.charite.de"
sender_email = "mcrc-db@charite.de"
receiver_email = "hannes.freitag@charite.de" 
password = input("Type your password and press enter:")

#context = ssl.create_default_context()
print("trying to connect")
mailserver = smtplib.SMTP_SSL(smtp_server,port, timeout=120)
print("connected")
mailserver.ehlo()
#mailserver.starttls(context= context)
mailserver.login(sender_email, password)
#Adding a newline before the body text fixes the missing message body
mailserver.send_mail(sender_email,receiver_email,'\npython email')
mailserver.quit()