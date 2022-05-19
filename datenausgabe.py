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

#Debugging
import traceback
import sys


df = pandas.DataFrame() 

def Analyse(parameters) -> pandas.DataFrame: 
    #Connect to Database
    global mydb
    mydb = mysql.connector.connect(host=os.environ.get('KRK_DB_HOST'),
                                           user=os.environ.get('KRK_DB_USER'),
                                           password=os.environ.get('KRK_DB_PASS'),
                                           database=os.environ.get('KRK_DB_DATABASE'))
    
    print(parameters)

    cursor= mydb.cursor()
    cursor.execute("SELECT * FROM mcrc_tabelle")
    myresult = cursor.fetchall()
    df = pandas.DataFrame(myresult)
    df.columns = Columns.d 

    #Entferne Spalten ohne Kürzel -> Entferne noch nicht bearbeitete Zeilen
    df.query("Kuerzel != ''", inplace=True)
    
    #Beginn des Filterns

    ##Check für SAPID

    if(parameters.get('pat_id_check', None)):
        if(parameters["pat_id"]):
            print(type(parameters["pat_id"]))
            pat_id = int(parameters['pat_id'])
            df.query("pat_id == @pat_id", inplace= True)
    
    ##Check for Geburtsdatum
    if(parameters.get('geburtcheck',None)):
        if(parameters['von_geburt']):
            von_geburt = datetime.datetime.strptime(parameters['von_geburt'], '%Y-%m-%d')
            von_geburt = datetime.date(von_geburt.year,von_geburt.month,von_geburt.day)
            print(von_geburt)
            df.query("dob >= @von_geburt",inplace=True)
        if(parameters["bis_geburt"]):
            bis_geburt = datetime.datetime.strptime(parameters['bis_geburt'], '%Y-%m-%d')
            bis_geburt = datetime.date(bis_geburt.year,bis_geburt.month,bis_geburt.day)
            df.query("dob <= @bis_geburt",inplace=True)

    ##Check for Sex
    if(parameters.get('sexcheck',None)):
        sexlist = []
        if(parameters.get('männlichcheck', None)): sexlist.append('m'); print("Männlich")
        if(parameters.get('weiblichcheck', None)): sexlist.append('f');print("weiblich")
        if(parameters.get('diverscheck', None)): sexlist.append('d');print("Divers")
        df.query("sex in @sexlist", inplace=True)

    ##Check for Diagnose Codes
    if(parameters.get("diagnose_code_check",None)):
        if(parameters['diagnosis1']):
            print(type(parameters['diagnosis1']))
            df.query("diagnosis1 == @parameters['diagnosis1']",inplace=True)
            print("checked for diagnosis1")
        if(parameters["diagnosis2"]):
            df.query("diagnosis2 == @parameters['diagnosis2']",inplace=True)
            print("checked for diagnosis2")

    ##CHeck for Diagnosis Date
    if(parameters.get("diagnosis_date_check",None)):
        if(parameters['von_diagnosis_date']):
            von_diagnosis_date = datetime.datetime.strptime(parameters['von_diagnosis_date'], '%Y-%m-%d')
            von_diagnosis_date = datetime.date(von_diagnosis_date.year,von_diagnosis_date.month,von_diagnosis_date.day)
            df.query("diagnosis_date >= @von_diagnosis_date",inplace=True)
        if(parameters["bis_diagnosis_date"]):
            bis_diagnosis_date = datetime.datetime.strptime(parameters['bis_diagnosis_date'], '%Y-%m-%d')
            bis_diagnosis_date = datetime.date(bis_diagnosis_date.year,bis_diagnosis_date.month,bis_diagnosis_date.day)
            df.query("diagnosis_date <= @bis_diagnosis_date",inplace=True)
    
    ##Check for Primary Location
    if(parameters.get('primary_location_check',None)):
        locations = []
        if(parameters.get('Rektum_check', None)): locations.append('Rektum')
        if(parameters.get('Sigma_check', None)): locations.append('Sigma')
        if(parameters.get('Descendens_check', None)): locations.append('Descendens')
        if(parameters.get('Transversum_check', None)): locations.append('Transversum')
        if(parameters.get('Ascendens_check', None)): locations.append('Ascendens')
        if(parameters.get('Zäkum_check', None)): locations.append('Zäkum')
        if(parameters.get('Rektosigmoid_check', None)): locations.append('Rektosigmoid')       
        df.query("primary_location in @locations", inplace=True)

    ##Check for Synchron/Metachron
    if(parameters.get('crlm_met_syn_check',None)):
        crlm_list = []
        if(parameters.get('Synchron_check', None)): crlm_list.append('synchron');print("synchron")
        if(parameters.get('Metachron_check', None)): crlm_list.append('metachron');print("metachron")
        df.query("crlm_met_syn in @crlm_list", inplace=True)

    ##check for Bilobulär#
    if(parameters.get('Bilobulär_check',None)):
        df.query("crlm_bilobular == 1", inplace=True) 
        print("inside bilobulär")
    
    ##Check for Multimodal
    if(parameters.get('Multimodal_check',None)):
        df.query("multimodal == 1", inplace=True) 
    
    ##Check for twostaged
    if(parameters.get('Two_staged_check',None)):
        df.query("two_staged == 1", inplace=True) 
       
    

    df.fillna("",inplace=True)
    return df