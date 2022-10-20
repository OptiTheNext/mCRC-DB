
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
context = ssl.create_default_context()

context = ssl.create_default_context()
with smtplib.SMTP(smtp_server, port) as server:
    server.ehlo()  # Can be omitted
    server.starttls(context=context)
    server.ehlo()  # Can be omitted
    server.login(sender_email, password)
    server.send_message(msg)