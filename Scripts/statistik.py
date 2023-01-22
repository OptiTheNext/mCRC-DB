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
import matplotlib.pyplot
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
import regex

import statsmodels.api as sm

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

labor_verlauf_liste = []

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
"two_staged",
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

labor_werte = [
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
    "th_INR_LAST"
]

global result

def table_one_func(x,loesung):
    lista = [[x]]
    print(loesung.values)
    for i,j in zip(loesung.axes[0].values.astype(str),loesung.values.astype(str)):
            lista = lista + [[i,j]]
            
    return lista
            

def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct*total/100.0))
        return '{p:.2f}%  ({v:d})'.format(p=pct,v=val)
    return my_autopct

def deskreptiv(df,points_of_interest,grafik,table_one):
    #Table one für Werte aus DF und Liste zur beschränkung der werte
    print("Wuhu, deskreptiv")
    print("Graphik =")
    print(grafik)
    print(table_one)
    df = pandas.DataFrame(df)
    print(points_of_interest)
    

    for x in points_of_interest:
        if x in to_drop:
            continue
            
        current_name = x
        current_df = df[x]
        current_df.dropna(inplace=True)
        
        if x in booleans:
            df = df.replace({0:False, 1:True})
            print("replaced with False/True")
            
        if x in decimals:
            print("trying to change formats")
            
            current_df = pandas.to_numeric(current_df)
            
        if x in categorials:
            current_df = current_df.astype(str)
            current_df[1] = current_df.replace("", numpy.nan, inplace=True)
            current_df[1] = current_df.dropna(inplace = True)
            
            
        print(current_df.dtype)
        if(table_one):
            result = current_df.describe()
            table = table_one_func(x,result)
            table = Table(table)
            global elements
            elements.append(table)
        if(grafik):
            print("ich bin unter if grafik")
            print(x)
            if x in booleans:
                print("ich bin in booleans")
                values = current_df.value_counts()
                print("ich printe values:")
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
        

    
def normalverteilung(df,points_of_interest,saphiro,kolmogorov,anderson,qqplot,histo):
    #Test auf Normalverteilung und entsprechender T-Test
    for x in points_of_interest:
        if x in decimals:
            # Vorbereitungen: Spalte rausziehen, zu numbern, leere spalten loswerden
            df = pandas.DataFrame(df)
            df = df[x]
            
            df = pandas.to_numeric(df)
            
            df = df[~numpy.isnan(df)]
            
            if(saphiro == True):
                result = scipy.stats.shapiro(df)
                lista = ([x," :Saphiro-Wilkoson Test"],["Teststatistik",result[0]],["P-Wert",result[1]])
                table = Table(lista)
                elements.append(table)
            if(kolmogorov == True):
                result = scipy.stats.kstest(df,'norm')
                lista = ([x," :Kolmogorov-Smirnov Test"],["Teststatistik",result[0]],["P-Wert",result[1]])
                table = Table(lista)
                elements.append(table)
            print("anderson")
            if(anderson == True):
                result=scipy.stats.anderson(df)
                lista = ([x," :Anderson-Test"],["Teststatistik",result[0]],["Kritische Werte",result[1]],["Signifikanslevel",result[2]])
                table = Table(lista)
                elements.append(table)
            if(qqplot == True):
                fig = sm.qqplot(df, line='45',xlabel='Zu erwartende Werte',ylabel=x)
                save_here = PATH_OUT + x +".png"
                fig.savefig(save_here) 
                elements.append(Image(save_here,width=8*reportlab.lib.units.cm, height=8*reportlab.lib.units.cm))
                fig.clf()
            if(histo == True):
                print("hier histo")
                fig, ax = matplotlib.pyplot.subplots()
                df.plot.kde(ax=ax, legend=False)
                df.plot.hist(density=True, ax=ax)
                ax.set_ylabel('Probability')
                ax.grid(axis='y')
                ax.set_facecolor('#d8dcd6')
                save_here = PATH_OUT + x+".png"
                fig.savefig(save_here) 
                elements.append(Image(save_here,width=8*reportlab.lib.units.cm, height=8*reportlab.lib.units.cm))
                fig.clf()





    print("Wuhu, normalverteilt")

def exploration(df, points_of_interest,reg_one,reg_two,linear, log):
    #Test / Darstellung von korrellation
    df = pandas.DataFrame(df)
    print(df)
    print("der eingegebene dataframe")
    labor_verlauf_liste = []
    global op_nm
    global labor_typ
    def verlauf_check(x): 
        if x in labor_werte:
                print("teste auf verlauf")
                global op_nm
                global labor_typ
                op_nm = x.split("_")[0]
                labor_typ = x.split("_")[1]
                my_regex = regex.escape(op_nm) + regex.escape(labor_typ)
                for s in labor_verlauf_liste:
                    print("in verlaufs schleife")
                    if regex.search(my_regex, s):
                        print("its true, verlauf bereits angelegt")
                        return True
                    else:
                        print('verlauf noch nicht angelegt')
                        labor_verlauf_liste.append(op_nm+labor_typ)
                        print(labor_verlauf_liste)
                        return False
                if not labor_verlauf_liste:
                    print('verlauf noch nicht angelegt')
                    labor_verlauf_liste.append(op_nm+labor_typ)
                    print(labor_verlauf_liste)
                    return False
    def lin_reg(row):
        print("linreg")
        ywerte = []
        xwerte = []
        row = pandas.to_numeric(row)
        print(type(row[0]))
        if not numpy.isnan(row[0]):
            ywerte.append(row[0])
            xwerte.append(1)
        if not numpy.isnan(row[1]):
            ywerte.append(row[1])
            xwerte.append(3)
        if not numpy.isnan(row[2]):
            ywerte.append(row[2])
            xwerte.append(5)
        if not numpy.isnan(row[3]):
            ywerte.append(row[3])
            xwerte.append(row[4])
        
        slope, intercept, r, p, se = scipy.stats.linregress(xwerte, y=ywerte, alternative='two-sided')
        return slope

    if linear:
        for x in point_of_interest:
            if verlauf_check(x):
                continue
            # now we need to create a new dataframe with all of the Data in linearer regression zum vergleich
            value = op_nm + "_"   
            if(labor_typ == "Serum" or labor_typ == "Drain"):
                    value = value + labor_typ + "_Bili"
            else:
                    value = value + labor_typ   
            valuepoint1 = value  + '_POD1'
            valuepoint2 = value  + '_POD3'
            valuepoint3 = value + '_POD5'
            valuepoint4 = value + '_Last'
            valuepoint5 = op_nm + "_los"

            df2 = df[[valuepoint1,valuepoint2,valuepoint3,valuepoint4,valuepoint5]] 
            df2.dropna(axis = 0, how = "all", inplace = True)
            
            #BEGINN DER REGRESSION! 
            df2['Slope'] = df2.apply(lin_reg, axis = 1)
            print(df2)

            #Hier table One
            df3 = df2['Slope']
            df3 = pandas.to_numeric(df3)

            result = df3.describe()

            listb = table_one_func(x,result)
            table = Table(listb)
            global elements
            elements.append(table)
            #Hier Boxplot
            pie = df3.plot.box(figsize=(8, 8))
            fig = pie.get_figure()
            save_here = PATH_OUT + x+".png"
            fig.savefig(save_here)  
            elements.append(Image(save_here,width=8*reportlab.lib.units.cm, height=8*reportlab.lib.units.cm))
            fig.clf()

            print(df2)
            
                








            
                    
            
    


    print("wuhu, explorativ")


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


