
import smtplib
from email.message import EmailMessage

#Hier noch passwort setzen
#https://betterdatascience.com/send-emails-with-python/
EMAIL_PASSWORD = ""

msg = EmailMessage()
msg['Subject'] = 'This is my first Python email'
msg['From'] = "mcrc-db@charite.de" 
msg['To'] = "hannes.freitag@charite.de" 
msg.set_content('And it actually works')


with smtplib.SMTP_SSL('email.charite.de', 587) as smtp:
    #hier noch nutzername setzen
    smtp.login("", EMAIL_PASSWORD) 
    smtp.send_message(msg)