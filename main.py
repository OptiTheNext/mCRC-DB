#Update with Git has worked
#Flask
import flask
import random
import json
from flask_session import Session
from flask import Flask, session
#Mysql
import mysql.connector
from mysql.connector import errorcode
import datetime
import os
from dotenv import load_dotenv
#Math
import pandas
import numpy
import matplotlib
import requests
import string
#Mails stuff
from exchangelib import DELEGATE, Account, Credentials, Configuration
import exchangelib
import jinja2
#Own Scripts
from Scripts import datenausgabe
from Scripts import generate_token
from Scripts import statistik
from Scripts import Columns
#Token
import jwt

#Debugging
import traceback
import sys

global sexbefore
sexbefore = False

load_dotenv()


querySAPID = "SELECT pat_id FROM mcrc_tabelle"
#Create an Flask app for the site to work on
app = flask.Flask(__name__,
                  template_folder="templates",
                  static_folder="static")

#For mail
mail_server = os.environ.get("KRK_DB_MAIL_SERVER")
mail_server = "https://" + mail_server
sender_mail = os.environ.get("KRK_DB_SENDER")
mail_user = os.environ.get("KRK_DB_MAIL_USER")
mail_password = os.environ.get("KRK_DB_MAIL_PASSWORD")
#Connect to Mail Service
print(mail_user)
print(mail_server)
print(mail_password)
print(sender_mail)
creds = Credentials(
    username=mail_user, 
    password=mail_password
)

config = Configuration(service_endpoint=mail_server, credentials=creds)

account = Account(
    primary_smtp_address=sender_mail,
    autodiscover=False, 
    config=config,
    access_type=DELEGATE
)

# Open HTML Template
with open('template.html', 'r') as f: 
        htmltext = f.read()
template = jinja2.Template(htmltext)

#For Token
app.secret_key = os.environ.get("KRK_APP_SECRET_KEY")
app.config['SESSION_TYPE'] = 'filesystem'
app.config["JWT_SECRET_KEY"]= os.environ.get("KRK_APP_SECRET_KEY")
#Create an App Session
Session(app)
#Create globe Renderparameters to copy from in the individual Sites
global RenderParameters
RenderParameters = {"Topnav":True,"startseite":True,"Admin": False}

#Connecting to ghe database in case of restart or lost connections
def connect_to_db():
    LocalRenderParameters = RenderParameters.copy()
    global mydb
    try:
        mydb = mysql.connector.connect(host=os.environ.get('KRK_DB_HOST'),
                                           user=os.environ.get('KRK_DB_USER'),
                                           password=os.environ.get('KRK_DB_PASS'),
                                           database=os.environ.get('KRK_DB_DATABASE'))
    except Exception as e:
        LocalRenderParameters["error"] = "Can't connect to Database, please inform Administrator"
        LocalRenderParameters["error-text"] = e
        return flask.render_template("login.html", RenderParameters = LocalRenderParameters)


global next_patient

#Workaround für ältere Browser
@app.route('/favicon.ico')
def favicon():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                                     'favicon.ico',
                                     mimetype='image/vnd.microsoft.icon')


@app.route('/android-chrome-192x192.png')
def favicon_chrome_192():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                                     'android-chrome-192x192.png')


@app.route('/android-chrome-256x256.png')
def favicon_chrome_256():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                                     'android-chrome-256x256.png')


@app.route('/browserconfig.xml')
def favicon_browserconfig():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                                     'browserconfig.xml')


@app.route('/apple-touch-icon.png')
def favicon_apple_touch():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                                     'apple-touch-icon.png')


@app.route('/mstile-150x150.png')
def favicon_mstile():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                                     'mstile-150x150.png')


@app.route('/safari-pinned-tab.svg')
def favicon_safari_pinned():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                                     'safari-pinned-tab.svg')


@app.route('/site.webmanifest')
def favicon_webmanifest():
    return flask.send_from_directory(os.path.join(app.root_path, 'static'),
                                     'site.webmanifest')


#Login Page
@app.route('/', methods=['POST', 'GET'])
def login():
    
    LocalRenderParameters = RenderParameters.copy()
    LocalRenderParameters["Topnav"] = False
    LocalRenderParameters["startseite"] = False
    LocalRenderParameters["Admin"] = False
    try:
        dbcursor=mydb.cursor()
    except Exception as e:
        connect_to_db()
        dbcursor= mydb.cursor()

    RenderParameters["error"] = ''
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        pwd = flask.request.form['password']
        try:
            select_query = "SELECT * FROM Users WHERE LoginID=%s AND Password=%s"
            dbcursor.execute(select_query, (username, pwd))
            selected_rows = dbcursor.fetchall()
            if(selected_rows):
                print(selected_rows)
                x = numpy.array(selected_rows)
                print(x[0,2])
                flask.session["username"] = username
                if (x[0,2] == "1"):
                    flask.session["Admin"] = True
                    RenderParameters["Admin"] = True
                else:
                    flask.session["Admin"] = False
                    RenderParameters["Admin"] = False

                
                return flask.redirect(flask.url_for('page_1'))
            else:
                LocalRenderParameters["error"] = 'Invalid Credentials. Please try again.'
        except Exception as e:
            print(e)
            #Exeption into Log Data
            LocalRenderParameters["error"] = 'Something went wrong, Contact a Server Administrator'
            LocalRenderParameters["error-text"] = e
    
    return flask.render_template("login.html", RenderParameters = LocalRenderParameters)

@app.route("/startseite")
def page_1():
    print(flask.session.get("Admin"))
    if ("username" in flask.session):
        LocalRenderParameters = RenderParameters.copy()
        LocalRenderParameters["startseite"] = False

        try:
            cursor= mydb.cursor()
            cursor.execute("SELECT COUNT(*) FROM mcrc_tabelle where Kuerzel=''")
            pat_to_do = cursor.fetchall()
            print(type(pat_to_do))
            print(pat_to_do[0][0])
            LocalRenderParameters["Pat_To_Do"] = pat_to_do[0][0]
        except Exception as e:
            print(e)
            print("No more patients to work on")


        return flask.render_template('site_1.html',
                                     RenderParameters = LocalRenderParameters)
        
    else:
        return flask.redirect(flask.url_for('login'))


@app.route("/dateneingabe", methods=["POST", "GET"])
def dateneingabe():
    if "username" not in flask.session:
        return flask.redirect(flask.url_for('login'))
    
    
    LocalRenderParameters = RenderParameters.copy()
    
    def get_next_patient_id(): 
        try:
            cursor= mydb.cursor()
            cursor.execute("SELECT mcrc_tabelle.pat_id FROM mcrc_tabelle WHERE mcrc_tabelle.Kuerzel = \"\" AND mcrc_tabelle.pat_id NOT IN (SELECT currently_active.pat_id FROM currently_active) ORDER BY mcrc_tabelle.op_date_Surgery1 DESC LIMIT 1")
            next_patient=cursor.fetchall()[0][0]
            print("Nächster Patient: ")
            print( next_patient)

            RenderParameters["next_patient"] = next_patient
            next_patient = None
        except Exception as e: 
            print("Neuer Patient konnte nicht ausgewählt werden")
            print(e)
           # send_error_mail(e, flask.session["username"])
            traceback.print_exc()
            next_patient = None

    get_next_patient_id()
    #Schreiben von daten
    print("Next is Grund")
    if "Grund" in flask.request.form:
        print("We are in Grund")
        print("Soll gelöscht werden: " + flask.request.form["Grund"])
        grund_to_delete = flask.request.form["Grund"]

        if "pat_id" in flask.request.form:
            pat_to_delete = flask.request.form["pat_id"]
            print(pat_to_delete + grund_to_delete)
            try:
                cursor = mydb.cursor()
            except Exception as e:
                LocalRenderParameters["Error"] = "Cannot reach database, contact administrator"
                LocalRenderParameters["error-text"] = e
                return flask.render_template('site_2.html',
                                      RenderParameters = LocalRenderParameters)


            try: 
                cursor.execute("INSERT INTO deleted_patients (id,reason) VALUES (%s,%s)",(pat_to_delete,grund_to_delete))
                mydb.commit()
                cursor.execute("DELETE FROM mcrc_tabelle WHERE pat_id = %s", (pat_to_delete,))
                mydb.commit()

                LocalRenderParameters = RenderParameters.copy()
                LocalRenderParameters["Success"] = "Deleted the username"
            except Exception as e:
                print("something went wrong")
                LocalRenderParameters["Error"] = "Nutzer kann nicht gelöscht werden"
                LocalRenderParameters["error-text"] = e
                
                #send_error_mail(e, flask.session["username"])
            


    if "Schreiben" in flask.request.form:
        print("In Input")
        if ("username" not in flask.session):
            return flask.redirect(flask.url_for('login'))

        if flask.request.method == 'POST':

            params = flask.request.form.to_dict(flat=True)
            print(params)
            p_columns = []
            p_values = []  
            
            opsgesamt = 0

            for item in params.items():
                if(item[1] == ""):
                    continue
                if(item[0] == "Schreiben"):
                    continue
                if(item[0] == "PreviousOPs"):
                    continue
                if(item[0] == "Chemo"):
                    continue
                if(item[0] == "LIMAX Count"):
                    continue
                if(item[0] == "diagnose2_check"):
                    continue
                if(item[0]== "pat_id_import"):
                    continue
                if(item[0]== "Löschen"):
                    continue    
                if(item[0]== "Grund"):
                    continue  
                if(item[0] == "secondOP_Check"):
                    continue
                if(item[0]=="thirdOP_Check"):
                    continue
                
                p_columns.append(item[0])
                p_values.append(item[1])
                
            if(params["op_date_Surgery1"] != "" and params["op_date_Surgery2"] != ""):
                p_columns.append("datediff_op1_op2")
                a = datetime.datetime.strptime(params["op_date_Surgery1"], "%Y-%m-%d")
                b = datetime.datetime.strptime(params["op_date_Surgery2"], "%Y-%m-%d")
                p_values.append(str((b-a).days))
            if(params["op_date_Surgery1"] != "" and params["dob"] != ""):
                p_columns.append("age")
                a = datetime.datetime.strptime(params["op_date_Surgery1"], "%Y-%m-%d")
                b = datetime.datetime.strptime(params["dob"], "%Y-%m-%d")
                c = (a-b).days / 365
                print("years: " + str(int(c)))
                p_values.append(str(int(c)))
                
            if(params["pve_date"] != ""):
                p_columns.append("pve_year")
                a = datetime.datetime.strptime(params["pve_date"], "%Y-%m-%d")
                a = a.year
                print(a)
                p_values.append(a)
            if(params["op_date_Surgery1"] != ""):
                p_columns.append("op1year")
                a= datetime.datetime.strptime(params["op_date_Surgery1"], "%Y-%m-%d")
                a = a.year
                p_values.append(a)
            
            
            if(params["op_date_Surgery1"]):
                opsgesamt = opsgesamt + 1 
            if(params["op_date_Surgery2"]):
                opsgesamt = opsgesamt + 1 
            if(params["op_date_Surgery3"]):
                opsgesamt = opsgesamt + 1 
            p_columns.append("surgeries")
            p_values.append(opsgesamt)

            #Setting defaults for checks
            if(params.get("crlm_bilobular",None) == None):
                p_columns.append("crlm_bilobular")
                p_values.append("0")
                print("in function for bilobulär")
            if(params.get("multimodal",None) == None):
                p_columns.append("multimodal")
                p_values.append("0")
            if(params.get("two_staged",None) == None):
                p_columns.append("two_staged")
                p_values.append("0")
            if(params.get("alcohol",None) == None):
                p_columns.append("alcohol")
                p_values.append("0")
            if(params.get("smoking",None) == None):
                p_columns.append("smoking")
                p_values.append("0")
            if(params.get("diabetes",None) == None):
                p_columns.append("diabetes")
                p_values.append("0")
            if(params.get("cirrhosis",None) == None):
                p_columns.append("cirrhosis")
                p_values.append("0")
            if(params.get("fibrosis",None) == None):
                p_columns.append("fibrosis")
                p_values.append("0")
            if(params.get("first_surgery_conversion", None) == None):
                p_columns.append("first_surgery_conversion")
                p_values.append("0")
            if(params.get("first_surgery_ablation", None) == None):
                p_columns.append("first_surgery_ablation")
                p_values.append("0")

            if(params["op_date_Surgery2"] and params.get("second_surgery_planned",None) == None):
                p_columns.append("second_surgery_planned")
                p_values.append("0")
            if(params["op_date_Surgery2"] and params.get("second_surgery_realized",None) == None):
                p_columns.append("second_surgery_realized")
                p_values.append("0")
            if(params.get("ss_previous_chemotherapy",None)==None and params["op_date_Surgery2"]):
                p_columns.append("ss_previous_chemotherapy")
                p_values.append("0")
            if(params.get("second_surgery_conversion", None) == None and params["op_date_Surgery2"]):
                p_columns.append("second_surgery_conversion")
                p_values.append("0")
            if(params.get("second_surgery_ablation", None) == None and params["op_date_Surgery2"]):
                p_columns.append("second_surgery_ablation")
                p_values.append("0")

            if(params["op_date_Surgery3"] and params.get("third_surgery_planned",None) == None):
                p_columns.append("third_surgery_planned")
                p_values.append("0")
            if(params["op_date_Surgery3"] and params.get("third_surgery_realized",None) == None):
                p_columns.append("third_surgery_realized")
                p_values.append("0")
            if(params.get("th_previous_chemotherapy",None)==None and params["op_date_Surgery3"]):
                p_columns.append("th_previous_chemotherapy")
                p_values.append("0")
            if(params.get("third_surgery_conversion", None) == None and params["op_date_Surgery3"]):
                p_columns.append("third_surgery_conversion")
                p_values.append("0")
            if(params.get("third_surgery_ablation", None) == None and params["op_date_Surgery3"]):
                p_columns.append("third_surgery_ablation")
                p_values.append("0")

            if(params.get("recurrence_date",None) or params.get("recurrence_organ",None)):
                p_columns.append("recurrence_status")
                p_values.append("1")
            else:
                p_columns.append("recurrence_status")
                p_values.append("0")
            if(params.get("pve_date",None)):
                p_columns.append("pve")
                p_values.append("1")
            else:
                p_columns.append("pve")
                p_values.append("0")

            
            print(p_columns)
            print( p_values)
            try:
                cursor = mydb.cursor()
            except Exception as e:
                LocalRenderParameters["Error"] = "Cannot reach database, contact administrator"
                LocalRenderParameters["error-text"] = e
                return flask.render_template('site_2.html',
                                      RenderParameters = LocalRenderParameters)
            cursor.execute(querySAPID)
            sid = cursor.fetchall()
            print(sid)
    
            #Insert the new data into the SQL Database
            try:
                cursor = mydb.cursor()
                p_columns.append("Kuerzel")
                p_values.append(f"{flask.session.get('username')}")
                print("------------------")
                #print((",".join(p_columns), ",".join(p_values)))
                statement = Columns.sql + "("
                for i in range(len(p_values)):
                    if i != 0:
                        statement += ","
                    statement += "%s"
                statement += ")"
                cursor.execute(statement.format(",".join(p_columns)), p_values)
                print(cursor.statement)
                mydb.commit()
                print(cursor._executed)
                print(cursor.statement)
                print(cursor.rowcount, "record inserted.")
                LocalRenderParameters["success"] = "Eingabe erfolgreich"

                #trying to delete from currently acitve
                try: 
                    cursor.execute("DELETE FROM currently_active WHERE pat_id = %s", (flask.request.form["pat_id"],))
                    mydb.commit()
                    print("deleted from currently active")
                except Exception as e:
                    print("nothing to delete") 
                    print(e)
                    
                get_next_patient_id()
                return flask.redirect(flask.url_for('dateneingabe'))

            except Exception as e:
                print(e)
                LocalRenderParameters["error"] = "Konnte nicht in die Datenbank geschrieben werden"
                LocalRenderParameters["error-text"] = e
                #send_error_mail(e, flask.session["username"])
                print("Fehler beim schreiben")
                #NotAllowed("Fehler", False)
                return flask.render_template('site_2.html',
                                      RenderParameters = LocalRenderParameters)
            #Merging both dataframes

        return flask.render_template('site_2.html',
                                      RenderParameters = LocalRenderParameters)

    
    #end of test for buttons
    return flask.render_template('site_2.html', RenderParameters = RenderParameters)


@app.route("/export")
def export_to_csv():
    if flask.session["df"]:
        dict_obj = session["df"]
        df = pandas.DataFrame(dict_obj)
        df = df.replace("","None")
        df = df.fillna("None")
        output = flask.make_response(df.to_csv(date_format="%d.%m.%Y", sep=";"))
        output.headers[
            "Content-Disposition"] = "attachment; filename=export.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    else:
        return flask.redirect(flask.url_for('page_3'))

@app.route("/export_statistik")
def export_statistik_as_pdf():
    pdf = flask.session["pdf_path"]
    
    #output = flask.make_response(pdf)
    #output.headers["Content.Disposition"] = "attachment; filename = statistik.pdf"
    #output.headers["Content-type"] = "application/pdf"
    #return output
    return flask.send_file(pdf, attachment_filename = "Statistik.pdf")
  


@app.route("/datenausgabe", methods=['POST', 'GET'])
def page_3():
    if ("username" in flask.session):
        LocalRenderParameters = RenderParameters.copy()
        # dateneingabelogik
        if "datenausgabe" in flask.request.form:
            print("hi")


            df = datenausgabe.Analyse(flask.request.form)
            dfdict = df.to_dict("list")
            flask.session['df'] = dfdict
            df.fillna("",inplace=True)
            #Darstellung der Tabelle
            cell_hover = {  # for row hover use <tr> instead of <td>
                'selector': 'td:hover',
                'props': [('background-color', '#ffffb3')]
            }
            index_names = {
                'selector': '.index_name',
                'props':
                'font-style: italic; color: darkgrey; font-weight:normal;'
            }
            headers = {
                'selector': 'th:not(.index_name)',
                'props': 'background-color: #000066; color: white;'
            }

            htmltext = flask.Markup(
                df.style.set_table_styles([
                    cell_hover,
                    index_names,
                    headers,
                    {
                        'selector': 'th.col_heading',
                        'props': 'text-align: center;'
                    },
                    {
                        'selector': 'th.col_heading.level0',
                        'props': 'font-size: 1.5em;'
                    },
                    {
                        'selector': 'td',
                        'props': 'text-align: center; font-weight: bold; border:solid'
                    },
                ],
                                          overwrite=False).to_html())
            
            LocalRenderParameters["htmltext"] = htmltext

            return flask.render_template('site_3.html', htmltext= htmltext, 
                                          RenderParameters = LocalRenderParameters)
            #weiterleitung zum Datenanalyse

        if "analysebutton" in flask.request.form:
                return flask.redirect(flask.url_for('page_4'))

        return flask.render_template('site_3.html',
                                      RenderParameters = LocalRenderParameters)
    else:
        return flask.redirect(flask.url_for('login'))


@app.route("/datenanalyse", methods=['POST', 'GET'])
def page_4():
    if ("username" in flask.session):
        LocalRenderParameters = RenderParameters.copy()
        return flask.render_template('site_4.html',
                                      RenderParameters = LocalRenderParameters)
    else:
        return flask.redirect(flask.url_for('login'))

@app.route("/datenanalyse_admin", methods = ["POST","GET"])
def page_4_admin():
    if ("username" in flask.session and flask.session.get("Admin") == 1):
        LocalRenderParameters = RenderParameters.copy()
        if(flask.session.get("df")):
            localDF = flask.session.get("df")
            LocalRenderParameters["df"] = True
        else: 
            try:
                cursor= mydb.cursor()
                cursor.execute("SELECT * FROM mcrc_tabelle where Kuerzel")
                localDF= cursor.fetchall()
            except Exception as e:
                LocalRenderParameters["Error"] = "Cannot reach database, contact administrator"
                LocalRenderParameters["error-text"] = e
                return flask.render_template('site_5.html',
                                      RenderParameters = LocalRenderParameters)
                
        if flask.request.method == 'GET':
            print(flask.request.args.to_dict(flat=False))
            if "csv_file" in flask.request.args:
                #Später anschauen
                print("hi")
        if flask.request.method == "POST":
            if flask.request.json:
                grafik = False
                table_one= False
                #statistik.deskreptiv(flask.session.get("df"),tags)
                print(flask.request.json)
                tags = flask.request.json["value"]
                print( tags)
                print(flask.request.form.get('table_one'))
                print("in table one")
                #Sammeln von Variablen für Deskriptiv

                if("table_one" in flask.request.json):
                    table_one = flask.request.json["table_one"]
                    print(flask.request.json)
                    if (table_one == True):
                        print("in table one = true")
                        table_one = True
                    if (table_one == "0"):
                        print("in table one = false")
                        table_one = False
                    print("hier table one")
                    print(table_one)

                if("grafik_deskriptiv" in flask.request.json):
                    grafik = flask.request.json["grafik_deskriptiv"]
                    print(grafik)
                    if (grafik == True):
                        grafik = True
                    if (grafik == "0"):
                        grafik = False
                    print(grafik)
                    
                
                statistik.deskreptiv(localDF,tags,grafik,table_one,)

                #Sammeln von Variablen für Normalverteilung
                if("saphiro" in flask.request.json):
                    saphiro = flask.request.json["saphiro"]
                    print(grafik)
                    if (saphiro == True):
                        saphiro = True
                    if (saphiro == "0"):
                        saphiro = False
                    print(saphiro)
                
                if("kolmogorov" in flask.request.json):
                    kolmogorov = flask.request.json["kolmogorov"]
                    print(grafik)
                    if (kolmogorov == True):
                        kolmogorov = True
                    if (kolmogorov == "0"):
                        kolmogorov = False
                    print(kolmogorov)

                if("anderson" in flask.request.json):
                    anderson = flask.request.json["anderson"]
                    print(grafik)
                    if (anderson == True):
                        anderson = True
                    if (anderson == "0"):
                        anderson = False
                    print(anderson)

                if("qq" in flask.request.json):
                    qq = flask.request.json["qq"]
                    print(grafik)
                    if (qq == True):
                        qq = True
                    if (qq == "0"):
                        qq = False
                    print(qq)

                
                if (saphiro or kolmogorov or anderson  or qq):
                    statistik.normalverteilung(localDF,tags,saphiro,kolmogorov,anderson,qq)

                #Sammeln von Variablen für Explorativ
                if("linear" in flask.request.json):
                    linear = flask.request.json["linear"]
                    print(grafik)
                    if (linear == True):
                        linear = True
                    if (linear == "0"):
                        linear = False
                    print(linear)
                if("log" in flask.request.json):
                    log = flask.request.json["log"]
                    print(grafik)
                    if (log == True):
                        log = True
                    if (log == "0"):
                        log = False
                    print(log)

                if (linear or log):
                    statistik.exploration(localDF,tags,linear,log)

                grafik = False
                table_one= False
                saphiro = False
                kolmogorov = False
                anderson = False
                qq = False 
                linear = False
                log = False
                
                pdf = statistik.generate_pdf()
                #flask.session["pdf_path"] = pdf
                print(pdf)
                flask.session["pdf_path"] = pdf
                return flask.redirect(flask.url_for("export_statistik_as_pdf"))
            
        return flask.render_template('site_4_admin.html',
                                      RenderParameters = LocalRenderParameters)
    else:
        return flask.redirect(flask.url_for('login'))

@app.route("/users", methods=['POST', 'GET'])
def page_5():
    LocalRenderParameters = RenderParameters.copy()
    def Usertext():
            try:
                cursor = mydb.cursor()
            except Exception as e:
                LocalRenderParameters["Error"] = "Cannot reach database, contact administrator"
                LocalRenderParameters["error-text"] = e
                return flask.render_template('site_5.html',
                                      RenderParameters = LocalRenderParameters)
            cursor.execute("SELECT * FROM Users")
            myresult = cursor.fetchall()
            df = pandas.DataFrame(myresult)
           
            df.columns= ['User', 'Password', 'Admin']
            df.Admin = df.Admin.replace({1: "yes", 0: "no"})
            df = df.drop(['Password'], axis=1)
         
            cell_hover = {  # for row hover use <tr> instead of <td>
                    'selector': 'td:hover',
                    'props': [('background-color', '#ffffb3')]
                }
            index_names = {
                    'selector': '.index_name',
                    'props':
                    'font-style: italic; color: darkgrey; font-weight:normal;'
                }
            headers = {
                    'selector': 'th:not(.index_name)',
                    'props': 'background-color: #000066; color: white;'
                }

            htmltext = flask.Markup(
                    df.style.set_table_styles([
                        cell_hover,
                        index_names,
                        headers,
                        {
                            'selector': 'th.col_heading',
                            'props': 'text-align: center;'
                        },
                        {
                            'selector': 'th.col_heading.level0',
                            'props': 'font-size: 1.5em;'
                        },
                        {
                            'selector': 'td',
                            'props': 'text-align: center; font-weight: bold;'
                        },
                    ],
                                            overwrite=False).to_html())
            return htmltext
    htmltext=Usertext() 
    LocalRenderParameters["htmltext"] = htmltext
    if ("username" in flask.session and flask.session.get("Admin")):
        

        if flask.request.method == 'POST':
            # Getting Name and If Admin
            if "create_user" in flask.request.form and "username" in flask.request.form and "mailadress" in flask.request.form:
                
                name = flask.request.form['username']
                mail = flask.request.form['mailadress']
                admin = flask.request.form['admin_select']
                #if("charite.de" not in mail):
                 #   LocalRenderParameters["error"] = 'Nutzer ist nicht Teil der Charité, Korrekte Mailadresse eingeben'
                  #  return flask.render_template('site_5.html',
                   #                            RenderParameters = LocalRenderParameters)
                if(admin == "Admin"):
                    admin = "1"
                else:
                    admin = "0"
                # Generating Link for password

                lower = string.ascii_lowercase
                upper = string.ascii_uppercase
                num = string.digits
                alll = lower + upper + num

                temp = random.sample(alll, random.randint(8, 12))
                
                password = "".join(temp)
                token = generate_token.generate_password_reset_token(name, password)
                print(type(token))
                #generate token for link:
                if(type(token) != str):
                    token = token.decode()

                url = flask.request.host_url + 'reset/'+ token
                print(url)

                #Von hier email senden
                m = exchangelib.Message(
                    account=account,
                    folder=account.sent,
                    subject='Vergeben Sie ein Passwort: mCRC',
                    body= exchangelib.HTMLBody(template.render({'name': name,"url":url})),
                    to_recipients=[exchangelib.Mailbox(email_address=mail)]
                )
                m.send_and_save()


                val = (name,password,admin)
                try:
                    cursor = mydb.cursor()
                    cursor.execute('INSERT INTO Users (LoginID, Password, Admin) VALUES (%s, %s, %s)', val)
                    mydb.commit()
                    return flask.render_template('site_5.html',
                                         RenderParameters = LocalRenderParameters)
                except Exception as e:
                    print(e)
                    LocalRenderParameters["error"] = "Couldnt enter user into Database, Contact an Administrator"
                    LocalRenderParameters["error-text"] = e
                   # send_error_mail(e, flask.session["username"])
                    return flask.render_template('site_5.html',
                                         RenderParameters = LocalRenderParameters)
                    
            
            if "delete_user" in flask.request.form and flask.request.form["delete_username"] != flask.session.get("username"):
                #deletuser
                print("trying to delete user")
                try:
                    cursor = mydb.cursor()
                    cursor.execute("DELETE FROM Users WHERE LoginID = %s", (flask.request.form["delete_username"],))
                    LocalRenderParameters["success"] ="Patient wurde aus der Datenbank entfernt"
                    return flask.render_template('site_5.html',
                                         RenderParameters = LocalRenderParameters)
                except Exception as e:
                    print(e)
                    LocalRenderParameters["error"] = "Couldnt delete user, Contact Administrator"
                    LocalRenderParameters["error-text"] = e
                   # send_error_mail(e, flask.session["username"])
                    return flask.render_template('site_5.html',
                                         RenderParameters = LocalRenderParameters)              
                
    if ("username" in flask.session):
            if "change_pwd" in flask.request.form:
                print("trying too change pwd")
                currentpw= flask.request.form["current_password"]
                newpwd= flask.request.form["new_password"]
                
                try:
                    cursor= mydb.cursor()
                    cursor.execute("SELECT * FROM Users WHERE LoginID = %s",(flask.session["username"],))
                    pwd = cursor.fetchone()[1]
                    print(pwd)
                    if (pwd == currentpw):
                        print("Yes, all correct")
                        cursor.execute("UPDATE Users SET Password = %s WHERE LoginID = %s",(newpwd, flask.session["username"]))
                        mydb.commit()
                        LocalRenderParameters["success"] ="Password was changed"
                        return flask.render_template('site_5.html',
                                         RenderParameters = LocalRenderParameters)
                    else:
                        LocalRenderParameters["error"] = 'Could not change password, current password was incorret'
                        return flask.render_template('site_5.html',
                                         RenderParameters = LocalRenderParameters)
                except Exception as e:
                     LocalRenderParameters["error"] = 'Could not write into Database, Contact an Admin for help'
                     LocalRenderParameters["error-text"] = e
                    # send_error_mail(e, flask.session["username"])
                     return flask.render_template('site_5.html',
                                        RenderParameters = LocalRenderParameters)

            
            return flask.render_template('site_5.html',
                                               RenderParameters = LocalRenderParameters)
    return flask.render_template('site_5.html',
                                         RenderParameters = LocalRenderParameters)

  

@app.route("/reset/<token>", methods=['POST', 'GET'])
def reset(token):
    LocalRenderParameters = RenderParameters.copy()
    LocalRenderParameters["Topnav"] = False
    LocalRenderParameters["startseite"] = False
    LocalRenderParameters["Admin"] = False
    try:
        decoded = jwt.decode(token, os.environ.get("KRK_APP_SECRET_KEY"), algorithms=["HS256"])
    except Exception as e:
        LocalRenderParameters["error"] = 'Your token is invalid, Please contact an Administrator'
        print(e)
        return flask.render_template("login.html", RenderParameters = LocalRenderParameters)
    print(decoded)

    ##Check for timestamp
    timestamp = datetime.datetime.fromtimestamp(decoded["exp"])
    print(type(timestamp))

    if(datetime.datetime.now() > timestamp):
         return flask.redirect(flask.url_for('login'))
    ##Check for username 
    try:
        dbcursor = mydb.cursor()
        select_query = "SELECT * FROM Users WHERE LoginID=%s AND Password=%s"
        dbcursor.execute(select_query, (decoded["username"], decoded["pwd"]))
        selected_rows = dbcursor.fetchall()
        print(selected_rows)
        if(selected_rows):
            if "Ändern" in flask.request.form:
                print("dabinich")
                passwort1= flask.request.form['password']
                passwort2 = flask.request.form['password_again']

                if(passwort1 == passwort2):
                    try:
                        cursor = mydb.cursor()
                        val = (decoded["username"],passwort1)
                        cursor.execute('REPLACE INTO Users (LoginID, Password) VALUES (%s, %s)', val)
                        mydb.commit()
                        return flask.redirect(flask.url_for('login'))
                    except Exception as e:
                        LocalRenderParameters["error"] = 'Could not write into Database, Contact an Admin for help'
                        LocalRenderParameters["error-text"] = e
                        #send_error_mail(e, flask.session["username"])
                        return flask.render_template('reset.html',
                                         RenderParameters = LocalRenderParameters) 

                else:
                     LocalRenderParameters["error"] = 'Passwords do not match, try again' 
            return flask.render_template('reset.html',
                                         RenderParameters = LocalRenderParameters) 
        else:
            return flask.redirect(flask.url_for('login'))
    except Exception as e:
        LocalRenderParameters["error"] = "Couldnt reach database, Contact Administrator"
        LocalRenderParameters["error-text"] = e
       # send_error_mail(e, flask.session["username"])
        return flask.redirect(flask.url_for('login'))
    



@app.route("/api/getDataForID", methods=['GET'])
def getDataForID():
    LocalRenderParameters = RenderParameters.copy()
    if flask.request.args["pat_id_import"]:
        try:
            cursor = mydb.cursor(dictionary=True, buffered = True)
        except Exception as e:
            return
        cursor.execute("SELECT * FROM mcrc_tabelle WHERE pat_id = %s", (flask.request.args["pat_id_import"],))
        if cursor.rowcount == 0:
            LocalRenderParameters["error"] = 'Patient not found in database' 
            return flask.render_template('site_2.html',
                                         RenderParameters = LocalRenderParameters) 
        for row in cursor:
            try:
                print("INSERT INTO currently_active (pat_id, timestamp) VALUES (%s,%s)" %(row.get("pat_id"),datetime.datetime.now()))
                cursor.execute("INSERT INTO currently_active (pat_id) VALUES (%s)",(row.get("pat_id"),))
                mydb.commit()
            except mysql.connector.Error as Error:
                print(Error)
                print("in mysql.connector.error")
                LocalRenderParameters["error"] = 'ID is currently being worked on, try again later' 
                return flask.render_template('site_2.html',
                                        RenderParameters = LocalRenderParameters)
            except Exception as e:
                print(e)
                LocalRenderParameters["error"] = 'Cannot connect to database, reach out to an Administrator' 
                return flask.render_template('site_2.html',
                                        RenderParameters = LocalRenderParameters)
            print(cursor.statement)
            print("entered the Currently Working thing into the DB")
            return app.response_class(response=json.dumps(row, default=str), mimetype='application/json')
    else:
            LocalRenderParameters["error"] = 'Error occured' 
            return flask.render_template('site_2.html',
                                        RenderParameters = LocalRenderParameters) 
    LocalRenderParameters["error"] = 'Error occured' 
    return flask.render_template('site_2.html',
                                         RenderParameters = LocalRenderParameters)

@app.route("/versions",methods = ["GET"])
def versions():
    LocalRenderParameters = RenderParameters.copy()
    return flask.render_template("site_6.html", RenderParameters = LocalRenderParameters)

@app.route("/api/tags", methods = ["GET"])
def tags_list():
    p = []
    for c,l in zip(Columns.d, Columns.b):
        q = {"value":c, "label":l}
        p.append(q)
    p = flask.jsonify(p)
    return p

if __name__ == '__main__':
  app.run(host=os.environ.get('KRK_APP_HOST'), port=os.environ.get('KRK_APP_PORT'), debug=True)
