# Flask
import datetime
import json
import os
import secrets
# Debugging
import traceback

import exchangelib
import flask
import jinja2
# Token
import jwt
# Mysql
import mysql.connector
import numpy
# Math
import pandas
from dotenv import load_dotenv
# Mails stuff
from exchangelib import DELEGATE, Account, Credentials, Configuration
from flask import session
from flask_session import Session

from Scripts import Columns
# Own Scripts
from Scripts import datenausgabe
from Scripts import generate_token
from Scripts import statistik
from Scripts import constants

global sexbefore
sexbefore = False

load_dotenv()

querySAPID = "SELECT pat_id FROM mcrc_tabelle"
# Create a Flask app for the site to work on
app = flask.Flask(__name__,
                  template_folder="templates",
                  static_folder="static")

# For mail
mail_server = "https://" + os.environ.get("KRK_DB_MAIL_SERVER")
sender_mail = os.environ.get("KRK_DB_SENDER")
mail_user = os.environ.get("KRK_DB_MAIL_USER")
mail_password = os.environ.get("KRK_DB_MAIL_PASSWORD")
# Connect to Mail Service
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

# For Token
app.secret_key = os.environ.get("KRK_APP_SECRET_KEY")
app.config['SESSION_TYPE'] = 'filesystem'
app.config["JWT_SECRET_KEY"] = os.environ.get("KRK_APP_SECRET_KEY")
# Create an App Session
Session(app)
# Create globe Renderparameters to copy from in the individual Sites
global RenderParameters
RenderParameters = {"Topnav": True, "startseite": True, "Admin": False}


app.config['UPLOAD_FOLDER'] = constants.UPLOAD_FOLDER


# Connecting to ghe database in case of restart or lost connections
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
        return flask.render_template(constants.URL_LOGIN, RenderParameters=LocalRenderParameters)


global next_patient


# Workaround für ältere Browser
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


# Login Page
@app.route('/', methods=['POST', 'GET'])
def login():
    LocalRenderParameters = RenderParameters.copy()
    LocalRenderParameters["Topnav"] = False
    LocalRenderParameters["startseite"] = False
    LocalRenderParameters["Admin"] = False
    try:
        dbcursor = mydb.cursor()
    except Exception as e:
        connect_to_db()
        dbcursor = mydb.cursor()

    RenderParameters["error"] = ''
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        pwd = flask.request.form['password']
        try:
            select_query = "SELECT * FROM Users WHERE LoginID=%s AND Password=%s"
            dbcursor.execute(select_query, (username, pwd))
            selected_rows = dbcursor.fetchall()
            if selected_rows:
                x = numpy.array(selected_rows)
                flask.session["username"] = username
                if x[0, 2] == "1":
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
            # Exeption into Log Data
            LocalRenderParameters["error"] = 'Something went wrong, Contact a Server Administrator'
            LocalRenderParameters["error-text"] = e

    return flask.render_template(constants.URL_LOGIN, RenderParameters=LocalRenderParameters)


@app.route("/startseite")
def page_1():
    print(flask.session.get("Admin"))
    if "username" in flask.session:
        LocalRenderParameters = RenderParameters.copy()
        LocalRenderParameters["startseite"] = False
        # FFind how many Patients are left to work on
        try:
            cursor = mydb.cursor()
            cursor.execute("SELECT COUNT(*) FROM mcrc_tabelle where Kuerzel=''")
            pat_to_do = cursor.fetchall()
            LocalRenderParameters["Pat_To_Do"] = pat_to_do[0][0]
        except Exception as e:
            print(e)
            print("No more patients to work on")
            LocalRenderParameters["Pat_To_Do"] = "Keine Verbindung zur Datenbank"

        return flask.render_template(constants.URL_STARTSEITE,
                                     RenderParameters=LocalRenderParameters)

    else:
        return flask.redirect(flask.url_for('login'))


@app.route("/dateneingabe", methods=["POST", "GET"])
def dateneingabe():
    if "username" not in flask.session:
        return flask.redirect(flask.url_for('login'))

    LocalRenderParameters = RenderParameters.copy()

    #Find an ID to work on next, without a Kürzel
    def get_next_patient_id():
        try:
            cursor = mydb.cursor()
            cursor.execute('SELECT mcrc_tabelle.pat_id FROM mcrc_tabelle WHERE mcrc_tabelle.Kuerzel = "" AND mcrc_tabelle.pat_id NOT IN (SELECT currently_active.pat_id FROM currently_active) ORDER BY mcrc_tabelle.op_date_Surgery1 DESC LIMIT 1')
            next_patient = cursor.fetchall()[0][0]
            RenderParameters["next_patient"] = next_patient
            next_patient = None
        except Exception as e:
            print("Neuer Patient konnte nicht ausgewählt werden")
            print(e)
            traceback.print_exc()
            next_patient = None

    get_next_patient_id()
    # Löschen von daten
    
    if "Grund" in flask.request.form:
        grund_to_delete = flask.request.form["Grund"]

        if "pat_id" in flask.request.form:
            pat_to_delete = flask.request.form["pat_id"]
            if pat_to_delete == "":
                pat_to_delete = flask.request.form["pat_id_import"]
            try:
                cursor = mydb.cursor()
            except Exception as e:
                LocalRenderParameters["Error"] = constants.ERRORTEXT_DATABASECONNECTION
                LocalRenderParameters["error-text"] = e
                return flask.render_template(constants.URL_DATENEINGABE,
                                             RenderParameters=LocalRenderParameters)

            try:

                #now into deleted_patients
                cursor.execute("INSERT INTO deleted_patients (id,reason) VALUES (%s,%s)",
                               (pat_to_delete, grund_to_delete))
                mydb.commit()
               #now deleteing from mcrc
                cursor.execute("DELETE FROM mcrc_tabelle WHERE pat_id = %s", (pat_to_delete,))
                mydb.commit()

                LocalRenderParameters = RenderParameters.copy()
                LocalRenderParameters["Success"] = "Deleted the ID"
            except Exception as e:
                print("something went wrong")
                print(e)
                LocalRenderParameters["Error"] = "ID kann nicht gelöscht werden"
                LocalRenderParameters["error-text"] = e

               

    if "Schreiben" in flask.request.form:
        if "username" not in flask.session:
            return flask.redirect(flask.url_for('login'))

        if flask.request.method == 'POST':

            params = flask.request.form.to_dict(flat=True)
        
            p_columns = []
            p_values = []

            opsgesamt = 0
            #Get rid of temporary variables from HTML 
            for item in params.items():
                if item[1] == "":
                    continue
                if item[0] == "Schreiben":
                    continue
                if item[0] == "PreviousOPs":
                    continue
                if item[0] == "Chemo":
                    continue
                if item[0] == "LIMAX Count":
                    continue
                if item[0] == "diagnose2_check":
                    continue
                if item[0] == "pat_id_import":
                    continue
                if item[0] == "Löschen":
                    continue
                if item[0] == "Grund":
                    continue
                if item[0] == "secondOP_Check":
                    continue
                if item[0] == "thirdOP_Check":
                    continue

                p_columns.append(item[0])
                p_values.append(item[1])
            #Set default Variables for dates
            if params["op_date_Surgery1"] != "" and params["op_date_Surgery2"] != "":
                p_columns.append("datediff_op1_op2")
                a = datetime.datetime.strptime(params["op_date_Surgery1"], constants.DATEFORMAT)
                b = datetime.datetime.strptime(params["op_date_Surgery2"], constants.DATEFORMAT)
                p_values.append(str((b - a).days))
            if params["op_date_Surgery1"] != "" and params["dob"] != "":
                p_columns.append("age")
                a = datetime.datetime.strptime(params["op_date_Surgery1"], constants.DATEFORMAT)
                b = datetime.datetime.strptime(params["dob"], constants.DATEFORMAT)
                c = (a - b).days / 365
                
                p_values.append(str(int(c)))

            if params["pve_date"] != "":
                p_columns.append("pve_year")
                a = datetime.datetime.strptime(params["pve_date"], constants.DATEFORMAT)
                a = a.year
            
                p_values.append(a)
            if params["op_date_Surgery1"] != "":
                p_columns.append("op1year")
                a = datetime.datetime.strptime(params["op_date_Surgery1"], constants.DATEFORMAT)
                a = a.year
                p_values.append(a)

            if params["op_date_Surgery1"]:
                opsgesamt = opsgesamt + 1
            if params["op_date_Surgery2"]:
                opsgesamt = opsgesamt + 1
            if params["op_date_Surgery3"]:
                opsgesamt = opsgesamt + 1
            p_columns.append("surgeries")
            p_values.append(opsgesamt)

            # Setting defaults for checks
            if params.get("crlm_bilobular", None) is None:
                p_columns.append("crlm_bilobular")
                p_values.append("0")
            if params.get("multimodal", None) is None:
                p_columns.append("multimodal")
                p_values.append("0")
            if params.get("two_staged", None) is None:
                p_columns.append("two_staged")
                p_values.append("0")
            if params.get("alcohol", None) is None:
                p_columns.append("alcohol")
                p_values.append("0")
            if params.get("smoking", None) is None:
                p_columns.append("smoking")
                p_values.append("0")
            if params.get("diabetes", None) is None:
                p_columns.append("diabetes")
                p_values.append("0")
            if params.get("cirrhosis", None) is None:
                p_columns.append("cirrhosis")
                p_values.append("0")
            if params.get("fibrosis", None) is None:
                p_columns.append("fibrosis")
                p_values.append("0")
            if params.get("first_surgery_conversion", None) is None:
                p_columns.append("first_surgery_conversion")
                p_values.append("0")
            if params.get("first_surgery_ablation", None) is None:
                p_columns.append("first_surgery_ablation")
                p_values.append("0")

            
            if params.get("fs_previous_chemotherapy", None) is None :
                p_columns.append("fs_previous_chemotherapy")
                p_values.append("0")

            if params["op_date_Surgery2"] and params.get("second_surgery_planned", None) is None:
                p_columns.append("second_surgery_planned")
                p_values.append("0")
            if params["op_date_Surgery2"] and params.get("second_surgery_realized", None) is None:
                p_columns.append("second_surgery_realized")
                p_values.append("0")
            if params.get("ss_previous_chemotherapy", None) is None and params.get("op_date_Surgery2",None):
                p_columns.append("ss_previous_chemotherapy")
                p_values.append("0")
            if params.get("second_surgery_conversion", None) is None and params["op_date_Surgery2"]:
                p_columns.append("second_surgery_conversion")
                p_values.append("0")
            if params.get("second_surgery_ablation", None) is None and params["op_date_Surgery2"]:
                p_columns.append("second_surgery_ablation")
                p_values.append("0")

            if params["op_date_Surgery3"] and params.get("third_surgery_planned", None) is None:
                p_columns.append("third_surgery_planned")
                p_values.append("0")
            if params["op_date_Surgery3"] and params.get("third_surgery_realized", None) is None:
                p_columns.append("third_surgery_realized")
                p_values.append("0")
            if params.get("th_previous_chemotherapy", None) is None and params.get("op_date_Surgery3",None):
                p_columns.append("th_previous_chemotherapy")
                p_values.append("0")
            if params.get("third_surgery_conversion", None) is None and params["op_date_Surgery3"]:
                p_columns.append("third_surgery_conversion")
                p_values.append("0")
            if params.get("third_surgery_ablation", None) is None and params["op_date_Surgery3"]:
                p_columns.append("third_surgery_ablation")
                p_values.append("0")

            if params.get("recurrence_date", None) or params.get("recurrence_organ", None):
                p_columns.append("recurrence_status")
                p_values.append("1")
            else:
                p_columns.append("recurrence_status")
                p_values.append("0")
            if params.get("pve_date", None):
                p_columns.append("pve")
                p_values.append("1")
            else:
                p_columns.append("pve")
                p_values.append("0")

            try:
                cursor = mydb.cursor()
            except Exception as e:
                LocalRenderParameters["Error"] = constants.ERRORTEXT_DATABASECONNECTION
                LocalRenderParameters["error-text"] = e
                return flask.render_template(constants.URL_DATENEINGABE,
                                             RenderParameters=LocalRenderParameters)
            cursor.execute(querySAPID)
            sid = cursor.fetchall()

            # Insert the new data into the SQL Database
            try:
                cursor = mydb.cursor()
                p_columns.append("Kuerzel")
                p_values.append(f"{flask.session.get('username')}")
                statement = Columns.sql + "("
                for i in range(len(p_values)):
                    if i != 0:
                        statement += ","
                    statement += "%s"
                statement += ")"
                cursor.execute(statement.format(",".join(p_columns)), p_values)
                mydb.commit()
                LocalRenderParameters["success"] = "Eingabe erfolgreich"

                # trying to delete from currently acitve
                try:
                    cursor.execute("DELETE FROM currently_active WHERE pat_id = %s", (flask.request.form["pat_id"],))
                    mydb.commit()
                except Exception as e:
                    print("nothing to delete")
                    print(e)

                get_next_patient_id()
                return flask.redirect(flask.url_for('dateneingabe'))

            except Exception as e:
                print(e)
                LocalRenderParameters["error"] = "Konnte nicht in die Datenbank geschrieben werden"
                LocalRenderParameters["error-text"] = e
                return flask.render_template(constants.URL_DATENEINGABE,
                                             RenderParameters=LocalRenderParameters)
            # Merging both dataframes

        return flask.render_template(constants.URL_DATENEINGABE,
                                     RenderParameters=LocalRenderParameters)

    # end of test for buttons
    return flask.render_template(constants.URL_DATENEINGABE, RenderParameters=RenderParameters)

#Generate a csv to export from current filtered data
@app.route("/export")
def export_to_csv():
    if flask.session["df"]:
        dict_obj = session["df"]
        df = pandas.DataFrame(dict_obj)
        df = df.replace("", "None")
        df = df.fillna("None")
        output = flask.make_response(df.to_csv(date_format="%d.%m.%Y", sep=";"))
        output.headers[
            "Content-Disposition"] = "attachment; filename=export.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    else:
        return flask.redirect(flask.url_for('page_3'))

# Export calculated statistic as pdf
@app.route("/export_statistik")
def export_statistik_as_pdf():
    LocalRenderParameters = RenderParameters
    pdf = flask.session["pdf_path"]
    try:
        return flask.send_file(pdf, download_name="Statistik.pdf")
    except Exception as e:
        LocalRenderParameters["Error"] = "Something went wrong, contact Administrator"
        LocalRenderParameters["error-text"] = e
        print(e)
        return flask.render_template(constants.URL_DATENANALYSE,
                                     RenderParameters=LocalRenderParameters)


@app.route("/datenausgabe", methods=['POST', 'GET'])
def page_3():
    if "username" in flask.session:
        LocalRenderParameters = RenderParameters.copy()
        if "datenausgabe" in flask.request.form:

            df = datenausgabe.analyse(flask.request.form)
            dfdict = df.to_dict("list")
            flask.session['df'] = dfdict
            df.fillna("", inplace=True)
            # Darstellung der Tabelle
            ##Set CSS Styles 
            cell_hover = {  # for row hover use <tr> instead of <td>
                'selector': 'td:hover',
                'props': [('background-color', '#ffffb3')]
            }
            index_names = {
                'selector': '.index_name',
                'props':
                    'font-style: italic; color: darkgrey; font-weight:normal;',

            }
            headers = {
                'selector': 'th:not(.index_name)',
                'props': 'background-color: #000999; color: white;',
                
            }

            df.columns = Columns.b
            df.drop(['Study ID', 'Case ID'], axis=1)
            #Change variables here for direct impact on table
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
                        'props': 'font-size: 1em;'
                    },
                    {
                        'selector': 'td',
                        'props': 'text-align: center; font-weight: bold; border:solid;'
                    },
                ],
                    overwrite=False).to_html())

            LocalRenderParameters["htmltext"] = htmltext

            return flask.render_template(constants.URL_DATENAUSGABE, htmltext=htmltext,
                                         RenderParameters=LocalRenderParameters)
            # weiterleitung zur Datenanalyse

        if "analysebutton" in flask.request.form:
            return flask.redirect(flask.url_for('page_4'))

        return flask.render_template(constants.URL_DATENAUSGABE,
                                     RenderParameters=LocalRenderParameters)
    else:
        return flask.redirect(flask.url_for('login'))


@app.route("/datenanalyse", methods=["POST", "GET"])
def page_4():
    if "username" in flask.session:

        LocalRenderParameters = RenderParameters.copy()
        if flask.session.get("df"):
            localDF = flask.session.get("df")
            LocalRenderParameters["df"] = True
        else:
            try:
                cursor = mydb.cursor()
                cursor.execute("SELECT * FROM mcrc_tabelle where Kuerzel")
                localDF = cursor.fetchall()
            except Exception as e:
                LocalRenderParameters["Error"] = constants.ERRORTEXT_DATABASECONNECTION
                LocalRenderParameters["error-text"] = e
                return flask.redirect(flask.url_for('datenausgabe'))
        if flask.request.method == "POST" and flask.request.json:
            flask.session["elements"] = []
            grafik = False
            table_one = False
            flask.session["pdf_completed"] = False
            tags = flask.request.json["server_tags"]
            reg_tags_one = flask.request.json["reg_tags_one"]
            reg_tags_two = flask.request.json["reg_tags_two"]
            # Collect and correctly set variables from html request
            #Collect variables for Deskriptive Statistik
            if "table_one" in flask.request.json:
                table_one = flask.request.json["table_one"]
                if table_one == True:
                    table_one = True
                if table_one == "0":
                    table_one = False

            if "grafik_deskriptiv" in flask.request.json:
                grafik = flask.request.json["grafik_deskriptiv"]
                if grafik == True:
                    grafik = True
                if grafik == "0":
                    grafik = False
            #If any variable is set, make the analysis
            if grafik or table_one:
                statistik.deskriptiv(localDF, tags, grafik, table_one)

            # Collect variables for Normalverteilung
            if "saphiro" in flask.request.json:
                saphiro = flask.request.json["saphiro"]
                if saphiro == True:
                    saphiro = True
                if saphiro == "0":
                    saphiro = False

            if "kolmogorov" in flask.request.json:
                kolmogorov = flask.request.json["kolmogorov"]
                if kolmogorov == True:
                    kolmogorov = True
                if kolmogorov == "0":
                    kolmogorov = False

            if "anderson" in flask.request.json:
                anderson = flask.request.json["anderson"]
                if anderson == True:
                    anderson = True
                if anderson == "0":
                    anderson = False

            if "qq" in flask.request.json:
                qq = flask.request.json["qq"]
                if qq == True:
                    qq = True
                if qq == "0":
                    qq = False
            if "histo" in flask.request.json:
                histo = flask.request.json["histo"]
                if histo == True:
                    histo = True
                if histo == "0":
                    histo = False
            #If any variable is set, make the analysis
            if saphiro or kolmogorov or anderson or qq or histo:
                statistik.normalverteilung(localDF, tags, saphiro, kolmogorov, anderson, qq, histo)

            # Sammeln von Variablen für Explorativ
            if "linear" in flask.request.json:
                linear = flask.request.json["linear"]
                if linear == True:
                    linear = True
                if linear == "0":
                    linear = False
            if "korrelation" in flask.request.json:
                korrelation = flask.request.json["korrelation"]
                if korrelation == True:
                    korrelation = True
                if korrelation == "0":
                    korrelation = False

            if "ttest_v" in flask.request.json:
                ttest_v = flask.request.json["ttest_v"]
                if ttest_v == True:
                    ttest_v = True
                if ttest_v == "0":
                    ttest_v = False
            if "ttest_unv" in flask.request.json:
                ttest_unv = flask.request.json["ttest_unv"]
                if ttest_unv == True:
                    ttest_unv = True
                if ttest_unv == "0":
                    ttest_unv = False
            if "utest" in flask.request.json:
                utest = flask.request.json["utest"]
                if utest == True:
                    utest = True
                if utest == "0":
                    utest = False
            if "will" in flask.request.json:
                will = flask.request.json["will"]
                if will == True:
                    will = True
                if will == "0":
                    will = False
            #This is not a boolean, just a variable to choose from
            mode_v = flask.request.json["Mode_v"]
            mode_unv = flask.request.json["Mode_unv"]
            mode_u = flask.request.json["Mode_u"]
            mode_w = flask.request.json["Mode_w"]

            #If any variable is set, make the analysis
            if linear or korrelation or ttest_v or ttest_unv or utest or will:
                statistik.exploration(localDF, tags, reg_tags_one, reg_tags_two, linear, korrelation, ttest_v,
                                      ttest_unv, utest, will,mode_unv,mode_v,mode_u,mode_w )
            #Reset Variables
            grafik = False
            table_one = False
            saphiro = False
            kolmogorov = False
            anderson = False
            qq = False
            linear = False
            log = False

            #Generate the PDF From the current results for the current user
            pdf = statistik.generate_pdf()
            flask.session["pdf_path"] = pdf
            flask.session["pdf_completed"] = True
            return flask.redirect(flask.url_for("export_statistik_as_pdf"))

        return flask.render_template(constants.URL_DATENANALYSE,
                                     RenderParameters=LocalRenderParameters)
    else:
        return flask.redirect(flask.url_for('login'))


@app.route("/users", methods=['POST', 'GET'])
def verwaltung():
    LocalRenderParameters = RenderParameters.copy()

    #Generate table with deleted patients
    def deleted_id_text():
        try:
            cursor = mydb.cursor()
        except Exception as e:
            LocalRenderParameters["Error"] = constants.ERRORTEXT_DATABASECONNECTION
            LocalRenderParameters["error-text"] = e
            return flask.render_template(constants.URL_VERWALTUNG,
                                         RenderParameters=LocalRenderParameters)
        cursor.execute("SELECT * FROM deleted_patients")
        myresult = cursor.fetchall()
        df = pandas.DataFrame(myresult)
        if df.empty:
            return
        df.columns = ['ID', 'Reason']

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
    #Generate Table with users
    def usertext():
        try:
            cursor = mydb.cursor()
        except Exception as e:
            LocalRenderParameters["Error"] = constants.ERRORTEXT_DATABASECONNECTION
            LocalRenderParameters["error-text"] = e
            return flask.render_template(constants.URL_VERWALTUNG,
                                         RenderParameters=LocalRenderParameters)
        cursor.execute("SELECT * FROM Users")
        myresult = cursor.fetchall()
        df = pandas.DataFrame(myresult)

        df.columns = ['User', 'Password', 'Admin']
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

    #Generate Tables with functions
    htmltext = usertext()
    deleted_id = deleted_id_text()
    LocalRenderParameters["htmltext"] = htmltext
    LocalRenderParameters["deleted_ids"] = deleted_id
    #If you are an admin you can edit the database from the Website
    if "username" in flask.session and flask.session.get("Admin"):

        if flask.request.method == 'POST':
            #Admin can create new users
            if "create_user" in flask.request.form \
                    and "username" in flask.request.form \
                    and "mailadress" in flask.request.form:

                name = flask.request.form['username']
                mail = flask.request.form['mailadress']
                #check if user has charite mail
                if "charite" not in mail:
                    LocalRenderParameters["Error"] = "Email muss eine Charite-Email sein"
                    LocalRenderParameters["error-text"] = e
                    return flask.render_template(constants.URL_VERWALTUNG,
                                         RenderParameters=LocalRenderParameters)

                admin = flask.request.form['admin_select']
                if admin == "Admin":
                    admin = "1"
                else:
                    admin = "0"
                # Generating Link for password
                password = secrets.token_urlsafe(secrets.SystemRandom().randint(a=8, b=16))
                token = generate_token.generate_password_reset_token(name, password)
                # generate token for link:
                if type(token) != str:
                    token = token.decode()

                url = flask.request.host_url + 'reset/' + token
                #Add user into database
                val = (name, password, admin)
                try:
                    cursor = mydb.cursor()
                    cursor.execute('INSERT INTO Users (LoginID, Password, Admin) VALUES (%s, %s, %s)', val)
                    mydb.commit()
                    return flask.render_template(constants.URL_VERWALTUNG,
                                                 RenderParameters=LocalRenderParameters)
                except Exception as e:
                    print(e)
                    LocalRenderParameters["error"] = "Couldnt enter user into Database, Contact an Administrator"
                    LocalRenderParameters["error-text"] = e
                    return flask.render_template(constants.URL_VERWALTUNG,
                                                 RenderParameters=LocalRenderParameters)

                # Sendind email to the new users
                m = exchangelib.Message(
                    account=account,
                    folder=account.sent,
                    subject='Vergeben Sie ein Passwort: mCRC',
                    body=exchangelib.HTMLBody(template.render({'name': name, "url": url})),
                    to_recipients=[exchangelib.Mailbox(email_address=mail)]
                )
                m.send_and_save()

            # deletuser
            if "delete_user" in flask.request.form and flask.request.form["delete_username"] != flask.session.get(
                    "username"):
                try:
                    cursor = mydb.cursor()
                    cursor.execute("DELETE FROM Users WHERE LoginID = %s", (flask.request.form["delete_username"],))
                    LocalRenderParameters["success"] = "Patient wurde aus der Datenbank entfernt"
                    return flask.render_template(constants.URL_VERWALTUNG,
                                                 RenderParameters=LocalRenderParameters)
                except Exception as e:
                    print(e)
                    LocalRenderParameters["error"] = "Couldnt delete user, Contact Administrator"
                    LocalRenderParameters["error-text"] = e

                    return flask.render_template(constants.URL_VERWALTUNG,
                                                 RenderParameters=LocalRenderParameters)

            if "add_id_to_db" in flask.request.form:
                # add id back into db
                try:
                    cursor = mydb.cursor()
                    cursor.execute("INSERT INTO mcrc_tabelle (pat_id) VALUES (%s)", (flask.request.form["id_to_add"],))
                    mydb.commit()
                    try:
                        cursor.execute("DELETE FROM deleted_patients WHERE id = %s", (flask.request.form["id_to_add"],))
                        mydb.commit()
                    except Exception as e:

                        LocalRenderParameters["Success"] = "Inserted the ID back into the DB"
                except Exception as e:
                    print(e)
                    LocalRenderParameters["error"] = "Couldnt add id into database, Contact Administrator"
                    LocalRenderParameters["error-text"] = e
                    return flask.render_template(constants.URL_VERWALTUNG,
                                                 RenderParameters=LocalRenderParameters)

            # get the uploaded file
            uploaded_file = flask.request.files['file']
            if uploaded_file.filename != '':
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
                # set the file path
                uploaded_file.save(file_path)
                # save the file
                csvData = pandas.read_csv(file_path, index_col=False)
                csvData = pandas.DataFrame(csvData)

                try:
                    cursor = mydb.cursor()
                    cursor.execute("SELECT * FROM mcrc_tabelle")
                    myresult = cursor.fetchall()
                    df = pandas.DataFrame(myresult)
                    df.columns = Columns.d

                except Exception as e:
                    LocalRenderParameters["error"] = 'No connection to Database, contact Administrator'
                    return flask.render_template(constants.URL_VERWALTUNG,
                                                 RenderParameters=LocalRenderParameters)

                df = df.apply(pandas.to_numeric, errors="ignore")
                list_to_add_to_DB = []
                for x in csvData["pat_id"]:
                    if x not in df["pat_id"].values:
                        list_to_add_to_DB.append(x)

                for row in list_to_add_to_DB:
                    cursor.execute("INSERT INTO mcrc_tabelle (pat_id) VALUES (%s)", (row,))

                    mydb.commit()
                import os

                for filename in os.listdir(flask.session["UPLOAD_FOLDER"]):
                    os.remove(filename)

    #Function if you are not an admin
    if "username" in flask.session:
        if "change_pwd" in flask.request.form:
            currentpw = flask.request.form["current_password"]
            newpwd = flask.request.form["new_password"]

            try:
                cursor = mydb.cursor()
                cursor.execute("SELECT * FROM Users WHERE LoginID = %s", (flask.session["username"],))
                pwd = cursor.fetchone()[1]
                if pwd == currentpw:
                    cursor.execute("UPDATE Users SET Password = %s WHERE LoginID = %s",
                                   (newpwd, flask.session["username"]))
                    mydb.commit()
                    LocalRenderParameters["success"] = "Password was changed"
                    return flask.render_template(constants.URL_VERWALTUNG,
                                                 RenderParameters=LocalRenderParameters)
                else:
                    LocalRenderParameters["error"] = 'Could not change password, current password was incorret'
                    return flask.render_template(constants.URL_VERWALTUNG,
                                                 RenderParameters=LocalRenderParameters)
            except Exception as e:
                LocalRenderParameters["error"] = 'Could not write into Database, Contact an Admin for help'
                LocalRenderParameters["error-text"] = e
                # send_error_mail(e, flask.session["username"])
                return flask.render_template(constants.URL_VERWALTUNG,
                                             RenderParameters=LocalRenderParameters)

        return flask.render_template(constants.URL_VERWALTUNG,
                                     RenderParameters=LocalRenderParameters)
    return flask.render_template(constants.URL_VERWALTUNG,
                                 RenderParameters=LocalRenderParameters)


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
        return flask.render_template(constants.URL_LOGIN, RenderParameters=LocalRenderParameters)

    ##Check for timestamp
    timestamp = datetime.datetime.fromtimestamp(decoded["exp"])

    if datetime.datetime.now() > timestamp:
        return flask.redirect(flask.url_for('login'))
    ##Check for username 
    try:
        dbcursor = mydb.cursor()
        select_query = "SELECT * FROM Users WHERE LoginID=%s AND Password=%s"
        dbcursor.execute(select_query, (decoded["username"], decoded["pwd"]))
        selected_rows = dbcursor.fetchall()
        if selected_rows:
            if "Ändern" in flask.request.form:
                passwort1 = flask.request.form['password']
                passwort2 = flask.request.form['password_again']

                if passwort1 == passwort2:
                    try:
                        cursor = mydb.cursor()
                        val = (decoded["username"], passwort1)
                        cursor.execute('REPLACE INTO Users (LoginID, Password) VALUES (%s, %s)', val)
                        mydb.commit()
                        return flask.redirect(flask.url_for('login'))
                    except Exception as e:
                        LocalRenderParameters["error"] = 'Could not write into Database, Contact an Admin for help'
                        LocalRenderParameters["error-text"] = e
                        return flask.render_template(constants.URL_RESET,
                                                     RenderParameters=LocalRenderParameters)

                else:
                    LocalRenderParameters["error"] = 'Passwords do not match, try again'
            return flask.render_template(constants.URL_RESET,
                                         RenderParameters=LocalRenderParameters)
        else:
            return flask.redirect(flask.url_for('login'))
    except Exception as e:
        LocalRenderParameters["error"] = constants.ERRORTEXT_DATABASECONNECTION
        LocalRenderParameters["error-text"] = e
        return flask.redirect(flask.url_for('login'))


@app.route("/api/getDataForID", methods=['GET'])
def get_data_for_id():
    LocalRenderParameters = RenderParameters.copy()
    if flask.request.args["pat_id_import"]:
        try:
            cursor = mydb.cursor(dictionary=True, buffered=True)
        except Exception as e:
            return
        cursor.execute("SELECT * FROM mcrc_tabelle WHERE pat_id = %s", (flask.request.args["pat_id_import"],))
        if cursor.rowcount == 0:
            LocalRenderParameters["error"] = 'Patient not found in database'
            return flask.render_template(constants.URL_DATENEINGABE,
                                         RenderParameters=LocalRenderParameters)
        for row in cursor:
            try:
                cursor.execute("INSERT INTO currently_active (pat_id) VALUES (%s)", (row.get("pat_id"),))
                mydb.commit()
            except mysql.connector.Error as Error:
                print(Error)
                print("in mysql.connector.error")
                LocalRenderParameters["error"] = 'ID is currently being worked on, try again later'
                return flask.render_template(constants.URL_DATENEINGABE,
                                             RenderParameters=LocalRenderParameters)
            except Exception as e:
                print(e)
                LocalRenderParameters["error"] = 'Cannot connect to database, reach out to an Administrator'
                return flask.render_template(constants.URL_DATENEINGABE,
                                             RenderParameters=LocalRenderParameters)
            print(cursor.statement)
            return app.response_class(response=json.dumps(row, default=str), mimetype='application/json')
    else:
        LocalRenderParameters["error"] = 'Error occured'
        return flask.render_template(constants.URL_DATENEINGABE,
                                     RenderParameters=LocalRenderParameters)
    LocalRenderParameters["error"] = 'Error occured'
    return flask.render_template(constants.URL_DATENEINGABE,
                                 RenderParameters=LocalRenderParameters)


@app.route("/versions", methods=["GET"])
def versions():
    LocalRenderParameters = RenderParameters.copy()
    return flask.render_template(constants.URL_VERSIONSVERLAUF, RenderParameters=LocalRenderParameters)


@app.route("/api/tags", methods=["GET"])
def tags_list():
    #A Function to give back tags from a json file on Statistik as a list so it can be worked on later
    p = []
    for c, l in zip(Columns.d, Columns.b):
        q = {"value": c, "label": l}
        p.append(q)
    p = flask.jsonify(p)
    return p


if __name__ == '__main__':
    app.run(host=os.environ.get('KRK_APP_HOST'), port=os.environ.get('KRK_APP_PORT'), debug=True)
