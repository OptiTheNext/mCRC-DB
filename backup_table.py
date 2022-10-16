import mysql.connector
import datetime
import os

from os import listdir
from os.path import isfile, join

from dotenv import load_dotenv
#Debugging
import traceback
import sys
import pandas
from Scripts import Columns

load_dotenv()

mydb = mysql.connector.connect(host=os.environ.get('KRK_DB_HOST'),
                                           user=os.environ.get('KRK_DB_USER'),
                                           password=os.environ.get('KRK_DB_PASS'),
                                           database=os.environ.get('KRK_DB_DATABASE'))

#Es macht sinn, die letzte update datei zu importieren, und wenn diese sich von dem aktuellem stand erst dann ein backup zu machen, ansonsten müllt die Festplatte so voll

onlyfiles = [f for f in listdir("./backups") if isfile(join("./backups", f))]
print(onlyfiles)
dates_to_check = []
for x in onlyfiles:
    date = x.split("_")[1]
    date = date.split(".")[0]
    date = datetime.datetime.strptime(date, "%b-%d-%Y")
    print (date)
    dates_to_check.append(date)

youngest = max(dt for dt in dates_to_check if dt < datetime.datetime.now())
print(youngest)

path_to_newest_file = "./backups/mcrc.table.backup_" + youngest.strftime("%b-%d-%Y") +".csv"
print(path_to_newest_file)

cursor = mydb.cursor()
df = cursor.execute("SELECT * FROM mcrc_tabelle")
myresult = cursor.fetchall()
df = pandas.DataFrame(myresult)
df.columns = Columns.d 
path = "./backups/mcrc.table.backup_" + datetime.date.today().strftime("%b-%d-%Y") +".csv"
df.to_csv(path,date_format="%d.%m.%Y", sep=";")

user = os.environ.get('KRK_DB_USER')
password = os.environ.get('KRK_DB_PASS')

os.system('mysqldump -u%s -p%s database > database.sql;' %(user,password))
        
mydb.disconnect()
