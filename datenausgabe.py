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
    
    ##Check for BRAF
    if(parameters.get('braf_check',None)):
        braf = []
        if(parameters.get('braf_mutiert_check', None)): braf.append('mut')
        if(parameters.get('braf_wildtyp_check', None)): braf.append('wt')
        df.query("BRAF in @braf", inplace=True)
    
    ##Check for RAS
    if(parameters.get('ras_check',None)):
        ras = []
        if(parameters.get('ras_mutiert_check', None)): ras.append('mut')
        if(parameters.get('ras_wildtyp_check', None)): ras.append('wt')
        df.query("RAS in @ras", inplace=True)
    
    ##Check for MSS
    if(parameters.get('mss_check',None)):
        mss = []
        if(parameters.get('mss', None)): mss.append('mut')
        if(parameters.get('msi', None)): mss.append('wt')
        df.query("MSS in @mss", inplace=True)

    ##Check for T
    if(parameters.get('t_check', None)):
        if(parameters["T"]):
            para = parameters['T']
            df.query("T == @para", inplace= True)
    
    ##Check for N
    if(parameters.get('n_check', None)):
        if(parameters["N"]):
            para = parameters['N']
            df.query("N == @para", inplace= True)
    
    #Check for M
    if(parameters.get('m_check', None)):
        if(parameters["M"]):
            para = parameters['M']
            df.query("M == @para", inplace= True)

    ##Check for LK
    if(parameters.get('lk_check', None)):
        if(parameters["LK"]):
            para = int(parameters['LK'])
            df.query("LK == @para", inplace= True)
    
    ##Check for L
    if(parameters.get('l_check', None)):
        if(parameters["L"]):
            para = int(parameters['L'])
            df.query("L == @para", inplace= True)
    
    ##Check for V
    if(parameters.get('v_check', None)):
        if(parameters["V"]):
            para = int(parameters['V'])
            df.query("V == @para", inplace= True)
    
    ##Check for R
    if(parameters.get('r_check', None)):
        if(parameters["R"]):
            para = int(parameters['R'])
            df.query("R == @para", inplace= True)

    ##Check for G
    if(parameters.get('g_check', None)):
        if(parameters["G"]):
            para = int(parameters['G'])
            df.query("G == @para", inplace= True)

    ##Check for Last Seen Date
    if(parameters.get("last_seen_check",None)):
        if(parameters['date_fu_von']):
            date_fu_von = datetime.datetime.strptime(parameters['date_fu_von'], '%Y-%m-%d')
            date_fu_von = datetime.date(date_fu_von.year,date_fu_von.month,date_fu_von.day)
            df.query("date_fu >= @date_fu_von",inplace=True)
        if(parameters["date_fu_bis"]):
            date_fu_bis = datetime.datetime.strptime(parameters['date_fu_bis'], '%Y-%m-%d')
            date_fu_bis = datetime.date(date_fu_bis.year,date_fu_bis.month,date_fu_bis.day)
            df.query("date_fu <= @date_fu_bis",inplace=True)

    ##Check for Alive or Not
    if(parameters.get("died_check",None)):
        if(parameters.get("died_no_check",None)):
             df.query("status_fu == 0",inplace=True)
        if(parameters.get("died_yes_check",None)):
             df.query("status_fu == 1",inplace=True)
    
    ##Check for Rezidiv
    if(parameters.get("rezidiv_check",None)):
        if(parameters.get("rezidiv_check_no",None)):
             df.query("recurrence_status == 0",inplace=True)
        if(parameters.get("rezidiv_check_yes",None)):
             df.query("recurrence_status == 1",inplace=True)

    ##Check for ASA
    if(parameters.get("asa_check",None)):
        if(parameters.get("asa_check_not_found",None)):
             df.query("ASA == 0",inplace=True)
        if(parameters.get("asa_check_1",None)):
             df.query("ASA == 1",inplace=True)
        if(parameters.get("asa_check_2",None)):
             df.query("ASA == 2",inplace=True)
        if(parameters.get("asa_check_3",None)):
             df.query("ASA == 3",inplace=True)
        if(parameters.get("asa_check_4",None)):
             df.query("ASA == 4",inplace=True)
        if(parameters.get("asa_check_5",None)):
             df.query("ASA == 5",inplace=True)
    
    ##Check for BMI
    if(parameters.get("bmi_check",None)):
        if(parameters["von_bmi_input"]):
            df.query("bmi == @parameters['von_bmi_input']", inpacte=True)
        if(parameters["bis_bmi_input"]):
            df.query("bmi == @parameters['bis_bmi_input']", inplace=True)
    
    ##Check for alc
    if(parameters.get("alc_check",None)):
        if(parameters.get("yes_alcohol_check",None)):
             df.query("alcohol == 0",inplace=True)
        if(parameters.get("no_alcohol_check",None)):
             df.query("alcohol == 1",inplace=True)

    ##Check for Raucher
    if(parameters.get("smoking_check",None)):
        if(parameters.get("smoking_check_yes",None)):
             df.query("smoking  == 0",inplace=True)
        if(parameters.get("smoking_check_no",None)):
             df.query("smoking  == 1",inplace=True)

    ##Check for Diabetiker
    if(parameters.get("diabetes_check",None)):
        if(parameters.get("diabetes_check_yes",None)):
             df.query("diabetes  == 0",inplace=True)
        if(parameters.get("diabetes_check_no",None)):
             df.query("diabetes  == 1",inplace=True)

    ##Check for Zirrose
    if(parameters.get("zirrose_check",None)):
        if(parameters.get("zirrose_check_yes",None)):
             df.query("cirrhosis   == 0",inplace=True)
        if(parameters.get("zirrose_check_no",None)):
             df.query("cirrhosis   == 1",inplace=True)

    ##Check for Fibrose
    if(parameters.get("fibrose_check",None)):
        if(parameters.get("fibrose_check_yes",None)):
             df.query("fibrosis == 0",inplace=True)
        if(parameters.get("fibrose_check_no",None)):
             df.query("fibrosis == 1",inplace=True)
    

    df.fillna("",inplace=True)
    return df