import flask
import random
import mysql.connector
import datetime
import Columns
import os
from dotenv import load_dotenv
import pandas
import numpy
import matplotlib
import requests
import string
import json
from flask_session import Session
from flask import Flask, session
from mailjet_rest import Client
import jwt
import scipy


app = flask.Flask(__name__,
                  template_folder="templates",
                  static_folder="static")

api_key = os.environ.get("KRK_DB_API_KEY")
print(api_key)

api_secret = os.environ.get("KRK_DB_SECRET_KEY")
mailjet = Client(auth=(api_key, api_secret), version='v3.1')

app.secret_key = os.environ.get("KRK_APP_SECRET_KEY")
app.config['SESSION_TYPE'] = 'filesystem'
app.config["JWT_SECRET_KEY"]= os.environ.get("KRK_APP_SECRET_KEY")
Session(app)



def deskreptiv(df,points_of_interest):
    #Table one für Werte aus DF und Liste zur beschränkung der werte
    print("Wuhu, deskreptiv")
    df = pandas.DataFrame(df)
    for x in points_of_interest:
        print(x)
        result = df[x].describe()
        print(result)
        #for objects here Kuchendiagramm
        #here we add it into the PDF

    
def normalverteilung(df):
    #Test auf Normalverteilung und entsprechender T-Test
    print(scipy.stats.shapiro(df))
    print("Wuhu, normalverteilt")

def korrellation(df):
    #Test / Darstellung von korrellation
    print("wuhu, korrellation")


##Hier wir nach dem Start für alle werte einmal statistik betrieben

def connect_to_db():
    global mydb
    try:
        mydb = mysql.connector.connect(host=os.environ.get('KRK_DB_HOST'),
                                           user=os.environ.get('KRK_DB_USER'),
                                           password=os.environ.get('KRK_DB_PASS'),
                                           database=os.environ.get('KRK_DB_DATABASE'))
    except Exception as e:
        print("Fehler!")

connect_to_db()

d = {'col1': [1, 2], 'col2': [3, 4]}
df = pandas.DataFrame(data=d)
point = ["col1",]
deskreptiv(df,point)
normalverteilung(df)