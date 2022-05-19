import mysql.connector
import datetime
import os
from dotenv import load_dotenv
#Debugging
import traceback
import sys

mydb = mysql.connector.connect(host=os.environ.get('KRK_DB_HOST'),
                                           user=os.environ.get('KRK_DB_USER'),
                                           password=os.environ.get('KRK_DB_PASS'),
                                           database=os.environ.get('KRK_DB_DATABASE'))

cursor = mydb.cursor()
cursor.execute("DELETE FROM currently_active WHERE timestamp < DATE_SUB(NOW(), INTERVAL 10 MINUTE)")
mydb.commit()
mydb.disconnect()

