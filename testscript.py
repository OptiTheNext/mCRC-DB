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
cursor.execute("REPLACE INTO mcrc_tabelle (pat_id,dob,sex,diagnosis1,primary_location,status_fu,Kuerzel) VALUES ('12','2022-04-25','f','12','Zäkum','0','HFreitag')")
mydb.commit()
print(cursor.statement)
print(cursor._executed)
rows = cursor.fetchall()
print(rows)
print(cursor.rowcount)
