import flask
import random
import mysql.connector
import datetime
from Scripts import Columns
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
from reportlab.pdfgen import canvas
import reportlab
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import *
from reportlab.lib import colors

from Scripts import datenausgabe

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

PATH_OUT="./"
styles = getSampleStyleSheet()
elements = []
elements.append(Paragraph("Hurensohn Title", styles['Title']))


to_drop = ["Kuerzel",
"pat_id",
"case_id",
"study_id",
"crlm_procedure_planned",
"crlm_procedure_realize",
"previous_surgery_which",
"fs_previous_chemotherapy_type",
"ss_previous_chemotherapy_type",
"th_previous_chemotherapy_type",
"first_surgery_type",
"second_surgery_type",
"third_surgery_type",
"fs_complication_which",
"ss_complication_which",
"ts_complication_which",
"Kommentar"
]


def deskreptiv(df,points_of_interest):
    #Table one für Werte aus DF und Liste zur beschränkung der werte
    print("Wuhu, deskreptiv")
    df = pandas.DataFrame(df)
    print(points_of_interest)
    for x in points_of_interest:
        if x in to_drop:
            continue
        current_df = df[x]
        current_df.dropna(inplace=True)
        print(current_df.dtype)
        result = current_df.describe()
        lista = [[x]]
        print(result.values)
        for i,j in zip(result.axes[0].values.astype(str),result.values.astype(str)):
           lista = lista + [[i,j[0]]]
        print(lista)
        table = Table(lista)
        global elements
        elements.append(table)

        if df[x].dtype == "object":
            print("Hier kuchendiagramm")

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
def generate_pdf():
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(PATH_OUT + 'Report_File.pdf')
    global elements
    doc.build(elements)
    elements = []
    elements.append(Paragraph("Hurensohn Title", styles['Title']))


## Statistik hier nach Neustart

df = datenausgabe.Analyse({})
df.replace('', numpy.nan, inplace=True)


#Zeilen die nicht ANALysiert werden sollen


##for x in Columns.d:
   
    
    # Deskriptive Statistik
    
    #Path = "/workspace/template-python-flask/Calculated_Descriptiv/" + x +".csv"
    
    #result.to_csv(Path)  


