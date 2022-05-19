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
            df.query("diagnosis1 == @parameters['diagnosis1']")
            print("checked for diagnosis1")
        if(parameters["diagnosis2"]):
            df.query("diagnosis2 == @parameters['diagnosis2']")
            print("checked for diagnosis2")
    print("hi")
    return df