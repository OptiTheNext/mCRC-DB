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

PATH_OUT="./Calculated_Statistic/"
styles = getSampleStyleSheet()
elements = []
elements.append(Paragraph("Statistische Auswertung", styles['Title']))


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
"Kommentar",
]

booleans = [
"alcohol",
"pve",
"RAS",
"BRAF",
"MSS",
"crlm_bilobular",
"multimodal",
"two_staged"
"status_fu",
"recurrence_status",
"smoking",
"diabetes",
"cirrhosis",
"fibrosis",
"previous_surgery",
"fs_previous_chemotherapy",
"first_surgery_ablation",
"first_surgery_conversion",
"seccond_surgery_planned",
"second_surgery_realized",
"ss_previous_chemotherapy",
"second_surgery_ablation",
"second_surgery_conversion",
"third_surgery_planned",
"third_surgery_realized",
"th_previous_chemotherapy",
"third_surgery_ablation",
"third_surgery_conversion"
]

decimals = [
    "limax_initial",
    "limax_second",
    "limax_third",
    "bmi",
    "limax_initial",
    "limax_second",
    "limax_third",
    "fs_previous_chemotherapy_cycles",
    "first_surgery_length",
    #Laborwerte
    ##Erste OP
    "fs_Serum_Bili_POD1",
    "fs_Serum_Bili_POD3",
    "fs_Serum_Bili_POD5",
    "fs_Serum_Bili_LAST",
    "fs_Drain_Bili_POD1",
    "fs_Drain_Bili_POD3",
    "fs_Drain_Bili_POD5",
    "fs_Drain_Bili_LAST",
    "fs_AST_POD1",
    "fs_AST_POD3",
    "fs_AST_POD5",
    "fs_AST_LAST",
    "fs_ALT_POD1",
    "fs_ALT_POD3",
    "fs_ALT_POD5",
    "fs_ALT_LAST",
    "fs_INR_POD1",
    "fs_INR_POD3",
    "fs_INR_POD5",
    "fs_INR_LAST",
    #Zweite OP
    "ss_Serum_Bili_POD1",
    "ss_Serum_Bili_POD3",
    "ss_Serum_Bili_POD5",
    "ss_Serum_Bili_LAST",
    "ss_Drain_Bili_POD1",
    "ss_Drain_Bili_POD3",
    "ss_Drain_Bili_POD5",
    "ss_Drain_Bili_LAST",
    "ss_AST_POD1",
    "ss_AST_POD3",
    "ss_AST_POD5",
    "ss_AST_LAST",
    "ss_ALT_POD1",
    "ss_ALT_POD3",
    "ss_ALT_POD5",
    "ss_ALT_LAST",
    "ss_INR_POD1",
    "ss_INR_POD3",
    "ss_INR_POD5",
    "ss_INR_LAST",
    #Dritte OP
    "th_Serum_Bili_POD1",
    "th_Serum_Bili_POD3",
    "th_Serum_Bili_POD5",
    "th_Serum_Bili_LAST",
    "th_Drain_Bili_POD1",
    "th_Drain_Bili_POD3",
    "th_Drain_Bili_POD5",
    "th_Drain_Bili_LAST",
    "th_AST_POD1",
    "th_AST_POD3",
    "th_AST_POD5",
    "th_AST_LAST",
    "th_ALT_POD1",
    "th_ALT_POD3",
    "th_ALT_POD5",
    "th_ALT_LAST",
    "th_INR_POD1",
    "th_INR_POD3",
    "th_INR_POD5",
    "th_INR_LAST",
    ##Neue Werte
    "fs_icu",
    "fs_los",
    "ss_previous_chemotherapy_cycles",
    "second_surgery_length",
    "ss_icu",
    "ss_los",
    "th_previous_chemotherapy_cycles",
    "third_surgery_length",
    "ts_icu",
    "ts_los",
    "age",
    "surgeries",
    "datediff_op1_op2"
]


ordinals = [
    "T",
    "N",
    "LK",
    "M",
    "G",
    "L",
    "V",
    "R"
    ]

categorials = [
    "diagnosis1",
    "diagnosis2",
    "op_code_Surgery1",
    "op_code_Surgery2",
    "op_code_Surgery3",
    "op_diagnosis_Surgery1",
    "op_diagnosis_Surgery2",
    "op_diagnosis_Surgery3",
    "sex",
    "primary_location",
    "RAS",
    "BRAF",
    "MSS",
    "crlm_met_syn",
    "crlm_bilobulär",
    "recurrence_organ",
    "asa",
    "fs_dindo",
    "ss_dindo",
    "ts_dindo"
]

dates = [
    "dob",
    "op_date_Surgery1",
    "op_date_Surgery2",
    "op_date_Surgery3",
    "pve_date",
    "diagnosis_date",
    "date_fu",
    "recurrence_date",
    "limax_initial_date",
    "limax_second_date",
    "limax_third_date",
    "previous_surgery_date",
]

def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.2f}%  ({v:d})'.format(p=pct,v=val)
    return my_autopct

def deskreptiv(df,points_of_interest,grafik,table_one):
    #Table one für Werte aus DF und Liste zur beschränkung der werte
    print("Wuhu, deskreptiv")
    df = pandas.DataFrame(df)
    print(points_of_interest)
    for x in points_of_interest:
        if x in to_drop:
            continue
        current_name = x
        current_df = df[x]
        current_df.dropna(inplace=True)
        print(current_df.dtype)
        if x in booleans:
            df = df.replace({0:False, 1:True})
            print("replaced with False/True")
            result = current_df.describe()
        if x in decimals:
            print("trying to change formats")
            print(df)
            current_df = pandas.to_numeric(current_df)
            result = current_df.describe()
        if x in categorials:
            current_df = current_df.astype(str)
            current_df[1] = current_df.replace("", numpy.nan, inplace=True)
            current_df[1] = current_df.dropna(inplace = True)
            result = current_df.describe()
            
        print(current_df.dtype)
        print(result)
        if(table_one):
            lista = [[x]]
            print(result.values)
            for i,j in zip(result.axes[0].values.astype(str),result.values.astype(str)):
                lista = lista + [[i,j]]
            print("Hier lista")
            print(lista)
            table = Table(lista)
            global elements
            elements.append(table)
        if(grafik):
            if x in booleans:
                values = current_df.value_counts()
                print(values)
                val = ['False:', 'True:']
                values = [values[0], values[1]]
                series2 = pandas.Series(values, 
                    index=val, 
                    name=current_name +"("+ str(sum(values))+")")
                pie = series2.plot.pie(figsize=(6, 6),autopct=make_autopct(values))
                fig = pie.get_figure()
                save_here = PATH_OUT + x+".png"
                fig.savefig(save_here)
                
                elements.append(Image(save_here,width=8*reportlab.lib.units.cm, height=8*reportlab.lib.units.cm))
                print(make_autopct((values)))
                fig.clf()
                values = None
                series2 = None
                print("Hier kuchendiagramm")

            if x in decimals:
                print("made an boxplot") 
                pie = current_df.plot.box(figsize=(6, 6))
                fig = pie.get_figure()
                save_here = PATH_OUT + x+".png"
                fig.savefig(save_here)  
                elements.append(Image(save_here,width=8*reportlab.lib.units.cm, height=8*reportlab.lib.units.cm))
                fig.clf()

            if x  in categorials:
                print ("making a Balkendiagramm")
                
                current_df=current_df.value_counts()
                print(current_df)
                pie = current_df.plot.bar(figsize = (6,6))
                fig = pie.get_figure()
                save_here = PATH_OUT + x+".png"
                fig.savefig(save_here)  
                elements.append(Image(save_here,width=8*reportlab.lib.units.cm, height=8*reportlab.lib.units.cm))
                fig.clf()

        

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
    path = PATH_OUT + 'Statistik-' + flask.session["username"] + ".pdf"
    doc = SimpleDocTemplate(path)
    global elements
    doc.build(elements)
    elements = []
    elements.append(Paragraph("Statistische Auswertung", styles['Title']))
    return (path)


## Statistik hier nach Neustart

df = datenausgabe.Analyse({})
df.replace('', numpy.nan, inplace=True)


#Zeilen die nicht ANALysiert werden sollen


##for x in Columns.d:
   
    
    # Deskriptive Statistik
    
    #Path = "/workspace/template-python-flask/Calculated_Descriptiv/" + x +".csv"
    
    #result.to_csv(Path)  


