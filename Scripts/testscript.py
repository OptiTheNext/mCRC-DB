import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

mydb = mysql.connector.connect(host=os.environ.get('KRK_DB_HOST'),
                               user=os.environ.get('KRK_DB_USER'),
                               password=os.environ.get('KRK_DB_PASS'),
                               database=os.environ.get('KRK_DB_DATABASE'))

cursor = mydb.cursor()
cursor.execute("SELECT * FROM mcrc_tablle WHERE limax_second_date = 1.1.2000")
mydb.commit()
rows = cursor.fetchall()
