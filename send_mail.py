from exchangelib import DELEGATE, Account, Credentials, Configuration
import exchangelib
import jinja2


#Hier noch passwort setzen
#https://betterdatascience.com/send-emails-with-python/
EMAIL_PASSWORD = ""

with open('template.html', 'r') as f: 
        htmltext = f.read()
template = jinja2.Template(htmltext)


username = "Hannes"
link = "google.com"


port = 587  # For starttls
smtp_server = "email.charite.de"
sender_email = "mcrc-db@charite.de"
receiver_email = "hannes.freitag@charite.de" 
password = input("Type your password and press enter:")


print("trying to connect")
#mailserver = smtplib.SMTP(smtp_server,port, timeout=120)
#print("connected")
#mailserver.ehlo()
#mailserver.starttls(context= context)
#mailserver.login(sender_email, password)
#Adding a newline before the body text fixes the missing message body
#mailserver.send_mail(sender_email,receiver_email,'\npython email')
#mailserver.quit()

#
# with smtplib.SMTP(smtp_server, port,timeout= 30) as server:
  #  server.starttls(context= context)
   # server.login(sender_email, password)
    #server.ehlo()
    ########################server.sendmail(sender_email, receiver_email, message.as_string())


creds = Credentials(
    username="mb-mcrcdb", 
    password=password
)

config = Configuration(service_endpoint="Hier Platzhalter einsetzen", credentials=creds)

account = Account(
    primary_smtp_address="mcrc-db@charite.de",
    autodiscover=False, 
    config=config,
    access_type=DELEGATE
)


m = exchangelib.Message(
    account=account,
    folder=account.sent,
    subject='Daily motivation',
    body= exchangelib.HTMLBody(template.render({'name': username,"url":link})),
    to_recipients=[exchangelib.Mailbox(email_address='hannes.freitag@charite.de')]
)
m.send_and_save()