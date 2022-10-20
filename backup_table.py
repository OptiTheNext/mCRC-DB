import mysql.connector
import datetime
import os
import sys

from os import listdir
from os.path import isfile, join

from dotenv import load_dotenv
#Debugging
import traceback
import sys
import pandas
from Scripts import Columns

load_dotenv()

try:
    mydb = mysql.connector.connect(host=os.environ.get('KRK_DB_HOST'),
                                           user=os.environ.get('KRK_DB_USER'),
                                           password=os.environ.get('KRK_DB_PASS'),
                                           database=os.environ.get('KRK_DB_DATABASE'))

except Exception as E:
    sys.exit(1)

#Es macht sinn, die letzte update datei zu importieren, und wenn diese sich von dem aktuellem stand erst dann ein backup zu machen, ansonsten müllt die Festplatte so voll

cursor= mydb.cursor()

onlyfiles = [f for f in listdir("./backups") if isfile(join("./backups", f))]
print(onlyfiles)
dates_to_check = []
for x in onlyfiles:
    date = x.split("_")[1]
    date = date.split(".")[0]
    date = datetime.datetime.strptime(date, "%b-%d-%Y")
    print (date)
    dates_to_check.append(date)

youngest = None

if len(dates_to_check):
    youngest = max(dt for dt in dates_to_check if dt < datetime.datetime.now())
    print(youngest)

    path_to_newest_file = "./backups/mcrc.table.backup_" + youngest.strftime("%b-%d-%Y") +".csv"
    print(path_to_newest_file)

last_updated = cursor.execute("SELECT update_time FROM information_schema.tables WHERE table_schema = 'mcrc_db' AND table_name = 'mcrc_tabelle';")
last_updated = cursor.fetchall()
#last_updated = last_updated[0][0].strftime("%b-%d-%Y")

print("Hier das datum")
print(last_updated)
print(youngest)

if( youngest == None or youngest < last_updated[0][0]):
    print("its true")

    user = os.environ.get('KRK_DB_USER')
    password = os.environ.get('KRK_DB_PASS')

    path = "./backups/mcrc.table.backup_" + datetime.date.today().strftime("%b-%d-%Y") +".sql"
    #os.system('mysqldump -u%s -p%s mcrc_db > %s' %(user,password,path))
    print("we did it")

       
mydb.disconnect()
