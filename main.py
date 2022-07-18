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



#Own Scripts
import datenausgabe
import generate_token

#Debugging
import traceback
import sys

global sexbefore
sexbefore = False

load_dotenv()

querySAPID = "SELECT pat_id FROM mcrc_tabelle"


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
global RenderParameters
RenderParameters = {"Topnav":True,"startseite":True,"Admin": False}

global mydb
mydb = mysql.connector.connect(host=os.environ.get('KRK_DB_HOST'),
                                           user=os.environ.get('KRK_DB_USER'),
                                           password=os.environ.get('KRK_DB_PASS'),
                                           database=os.environ.get('KRK_DB_DATABASE'))

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


@app.route('/', methods=['POST', 'GET'])
def login():
    LocalRenderParameters = RenderParameters.copy()
    LocalRenderParameters["Topnav"] = False
    LocalRenderParameters["startseite"] = False
    LocalRenderParameters["Admin"] = False
    dbcursor=mydb.cursor()
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
    
    return flask.render_template("login.html", RenderParameters = LocalRenderParameters)

@app.route("/startseite")
def page_1():
    print(flask.session.get("Admin"))
    if ("username" in flask.session):
        LocalRenderParameters = RenderParameters.copy()
        LocalRenderParameters["startseite"] = False
        return flask.render_template('site_1.html',
                                     RenderParameters = LocalRenderParameters)
        
    else:
        return flask.redirect(flask.url_for('login'))


@app.route("/dateneingabe", methods=["POST", "GET"])
def dateneingabe():
    if "username" not in flask.session:
        return flask.redirect(flask.url_for('login'))
    
    cursor= mydb.cursor()
    try:
        cursor.execute("SELECT mcrc_tabelle.pat_id FROM mcrc_tabelle WHERE mcrc_tabelle.Kuerzel = \"\" AND mcrc_tabelle.pat_id NOT IN (SELECT currently_active.pat_id FROM currently_active) LIMIT 1")
        next_patient=cursor.fetchall()[0][0]
        print(next_patient)
        RenderParameters["next_patient"] = next_patient
    except Exception as e: 
        print("hat halt net geklappt")
        print(e)
        traceback.print_exc()
        next_patient = None

    #Schreiben von daten

    if "Schreiben" in flask.request.form:
        print("In Input")
        if ("username" not in flask.session):
            return flask.redirect(flask.url_for('login'))

        if flask.request.method == 'POST':
            
            params = flask.request.form.to_dict(flat=True)
            print(params)
            p_columns = []
            p_values = []  
            
            opgesamt = 0

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
                
                p_columns.append(item[0])
                p_values.append(item[1])
                
            if(params["op_date_Surgery1"] != "" and params["op_date_Surgery2"] != ""):
                p_columns.append("datediff_op1_op2")
                a = datetime.datetime.strptime(params["op_date_Surgery1"], "%Y-%m-%d")
                b = datetime.datetime.strptime(params["op_date_Surgery2"], "%Y-%m-%d")
                p_values.append(str((a-b).days))
            if(params["op_date_Surgery1"] != "" and params["dob"] != ""):
                p_columns.append("age")
                a = datetime.datetime.strptime(params["op_date_Surgery1"], "%Y-%m-%d")
                b = datetime.datetime.strptime(params["dob"], "%Y-%m-%d")
                p_values.append(str((a-b).days))
            if(params["pve_date"] != ""):
                p_columns.append("pve_year")
                a = datetime.datetime.strptime(params["pve_date"], "%Y")
                p_values.append(a)
            if(params["op_date_Surgery1"] != ""):
                p_columns.append("op1year")
                a= datetime.datetime.strptime(params["op_date_Surgery1"],"%Y")
                p_values.append(a)
            
            if(params["op_date-Surgery1"]):
                opsgesamt = opgesamt + 1 
            if(params["op_date-Surgery2"]):
                opsgesamt = opgesamt + 1 
            if(params["op_date-Surgery3"]):
                opsgesamt = opgesamt + 1 
            p_columns.append("surgeries")
            p_values.append(opgesamt)
            
            print(p_columns)
            print( p_values)
                    
            cursor = mydb.cursor()
            cursor.execute(querySAPID)
            sid = cursor.fetchall()
            print(sid)
    
            #Insert the new data into the SQL Database
            try:
                cursor = mydb.cursor()
                p_columns.append("Kuerzel")
                p_values.append(f"{flask.session.get('username')}")
                print("------------------")
                print((",".join(p_columns), ",".join(p_values)))
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
                RenderParameters["success"] = "Eingabe erfolgreich"

                #trying to delete from currently acitve
                try: 
                    cursor.execute("DELETE pat_id FROM currently_active WHERE patid = %s", (statement.get("pat_id"),))
                    mydb.commit()
                except Exception as e:
                    print("nothing to delete") 

                return flask.render_template('site_2.html',
                                            RenderParameters = RenderParameters
                                             )

            except Exception as e:
                print(e)
                RenderParameters["error"] = "Konnte nicht in die Datenbank geschrieben werden"
                #NotAllowed("Fehler", False)
                return flask.render_template(
                    'site_2.html',
                     RenderParameters = RenderParameters)
            #Merging both dataframes

        return flask.render_template('site_2.html',
                                      RenderParameters = RenderParameters)

    
    #end of test for buttons
    return flask.render_template('site_2.html', RenderParameters = RenderParameters)


@app.route("/export")
def export_to_csv():
    if flask.session["df"]:
        dict_obj = session["df"]
        df = pandas.DataFrame(dict_obj)
        
        output = flask.make_response(df.to_csv(date_format="%d.%m.%Y"))
        output.headers[
            "Content-Disposition"] = "attachment; filename=export.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    else:
        return flask.redirect(flask.url_for('page_3'))


@app.route("/datenausgabe", methods=['POST', 'GET'])
def page_3():
    if ("username" in flask.session):
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
                        'props': 'text-align: center; font-weight: bold;'
                    },
                ],
                                          overwrite=False).to_html())
            
            RenderParameters["htmltext"] = htmltext

            return flask.render_template('site_3.html', htmltext= htmltext, 
                                          RenderParameters = RenderParameters)
            #weiterleitung zum Datenanalyse
            if "analysebutton" in flask.request.form:
                # Datenbankvariable zur analyse noch setzen
                return flask.redirect(flask.url_for('page_4'))

        return flask.render_template('site_3.html',
                                      RenderParameters = RenderParameters)
    else:
        return flask.redirect(flask.url_for('login'))


@app.route("/datenanalyse", methods=['POST', 'GET'])
def page_4():
    if ("username" in flask.session):
        return flask.render_template('site_4.html',
                                      RenderParameters = RenderParameters)
    else:
        return flask.redirect(flask.url_for('login'))

@app.route("/users", methods=['POST', 'GET'])
def page_5():
    LocalRenderParameters = RenderParameters.copy()
    def Usertext():
            cursor = mydb.cursor()
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
            if "create_user" in flask.request.form:
                
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
                print(token)
                #generate token for link:
                url = flask.request.host_url + 'reset/'+ token
                print(url)
                data = {
                    'Messages': [
                        {
                        "From": {
                            "Email": "mcrc.cvk@gmail.com",
                            "Name": "Kolorektale Datenbank Charite"
                        },
                        "To": [
                            {
                            "Email": mail,
                            "Name": name
                            }
                        ],
                        #"HTMLPart": "<!DOCTYPE html> <html> <head> <title>Password Reset</title> </head><body> <div>  <h3>Dear {},</h3><p>Your password must be set, please follow this link: <a href=\'{}\'>Passwort</a></p><br> <div> Cheers!</div></div></body></html>".format(name, url),
                        "TemplateID": 4060819,
                        "Subject": "Passwort setzen für Kolorektale Datenbank",
                        "Variables": {
        
								"name": name,
								"url": url
						}
                        }
                    ]
                    }
                result = mailjet.send.create(data=data)
                print (result.status_code)
                print (result.json())

                
                
                val = (name,password,admin)
                try:
                    cursor = mydb.cursor()
                    cursor.execute('INSERT INTO Users (LoginID, Password, Admin) VALUES (%s, %s, %s)', val)
                    mydb.commit()
                    return flask.render_template('site_5.html',
                                         RenderParameters = LocalRenderParameters)
                except Exception as e:
                    print(e)
                    return flask.render_template('site_5.html',
                                         RenderParameters = LocalRenderParameters)
                    
            
            if "delete_user" in flask.request.form and flask.request.form["delete_username"] != flask.session.get("username"):
                #deletuser
                print("trying to delete user")
                try:
                    cursor = mydb.cursor()
                    cursor.execute("DELETE FROM Users WHERE LoginID = %s", (flask.request.form["delete_username"],))
                    return flask.render_template('site_5.html',
                                         RenderParameters = LocalRenderParameters)
                except Exception as e:
                    print(e)
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
    decoded = jwt.decode(token, os.environ.get("KRK_APP_SECRET_KEY"), algorithms=["HS256"])
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
                        return flask.render_template('reset.html',
                                         RenderParameters = LocalRenderParameters)
                    except Exception as e:
                        LocalRenderParameters["error"] = 'Could not write into Database, Contact an Admin for help'
                        return flask.render_template('reset.html',
                                         RenderParameters = LocalRenderParameters) 

                else:
                     LocalRenderParameters["error"] = 'Passwords do not match, try again' 
            return flask.render_template('reset.html',
                                         RenderParameters = LocalRenderParameters) 
        else:
            return flask.redirect(flask.url_for('login'))
    except Exception as e:
        print("Upsi, fehler")
        return flask.redirect(flask.url_for('login'))
    



@app.route("/api/getDataForID", methods=['GET'])
def getDataForID():
    if flask.request.args["pat_id_import"]:
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM mcrc_tabelle WHERE pat_id = %s", (flask.request.args["pat_id_import"],))
        if cursor.rowcount == 0:
            return "Requested ID not found in database"
        for row in cursor:
            print("INSERT INTO currently_active (pat_id, timestamp) VALUES (%s,%s)" %(row.get("pat_id"),datetime.datetime.now()))
            cursor.execute("INSERT INTO currently_active (pat_id) VALUES (%s)",(row.get("pat_id"),))
            mydb.commit()
            print(cursor.statement)
            print("entered the Currently Working thing into the DB")
            return app.response_class(response=json.dumps(row, default=str), mimetype='application/json')
    else:
        return "Request error"

if __name__ == '__main__':
  app.run(host=os.environ.get('KRK_APP_HOST'), port=os.environ.get('KRK_APP_PORT'), debug=True)
