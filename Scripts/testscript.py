import random
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

mydb = mysql.connector.connect(host=os.environ.get('KRK_DB_HOST'),
                                           user=os.environ.get('KRK_DB_USER'),
                                           password=os.environ.get('KRK_DB_PASS'),
                                           database=os.environ.get('KRK_DB_DATABASE'))

cursor = mydb.cursor()
cursor.execute("SELECT * FROM mcrc_tablle WHERE limax_second_date = 1.1.2000")
mydb.commit()
print(cursor.statement)
print(cursor._executed)
rows = cursor.fetchall()
print(rows)
print(cursor.rowcount)
