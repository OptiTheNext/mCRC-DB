import mysql.connector
import datetime
import os
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

cursor = mydb.cursor()
df = cursor.execute("SELECT * FROM mcrc_tabelle")
myresult = cursor.fetchall()
df = pandas.DataFrame(myresult)
df.columns = Columns.d 
df.to_csv("./backups/mcrc_table.csv",date_format="%d.%m.%Y", sep=";")
        
mydb.disconnect()
