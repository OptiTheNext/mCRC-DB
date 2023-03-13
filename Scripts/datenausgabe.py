import datetime
import os

import mysql.connector
import pandas
from dotenv import load_dotenv

from Scripts import Columns
from Scripts import constants

# Debugging


df = pandas.DataFrame()

load_dotenv()

df_AND = pandas.DataFrame()
df_or = pandas.DataFrame()
Mode = True
para = ""
paralist = []
von_date = ""
bis_date = ""


def analyse(parameters) -> pandas.DataFrame:
    # Connect to Database
    global mydb
    global para
    global paralist
    global von_date
    global bis_date

    mydb = mysql.connector.connect(host=os.environ.get('KRK_DB_HOST'),
                                   user=os.environ.get('KRK_DB_USER'),
                                   password=os.environ.get('KRK_DB_PASS'),
                                   database=os.environ.get('KRK_DB_DATABASE'))

    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM mcrc_tabelle")
    myresult = cursor.fetchall()
    df = pandas.DataFrame(myresult)
    df.columns = Columns.d

    # Convert Booleans into Python Booleans

    df = df.apply(pandas.to_numeric, errors="ignore")
    df['pve'] = df['pve'].astype('bool')
    df['dob'] = pandas.to_datetime(df.dob)
    df['crlm_bilobular'] = df['crlm_bilobular'].astype('bool')
    df['multimodal'] = df['multimodal'].astype('bool')
    df['two_staged'] = df['two_staged'].astype('bool')
    df['status_fu'] = df['status_fu'].astype('bool')
    df['recurrence_status'] = df['recurrence_status'].astype('bool')
    df['alcohol'] = df['alcohol'].astype('bool')
    df['smoking'] = df['smoking'].astype('bool')
    df['cirrhosis'] = df['cirrhosis'].astype('bool')
    df['fibrosis'] = df['fibrosis'].astype('bool')
    df['fs_previous_chemotherapy'] = df['fs_previous_chemotherapy'].astype('bool')
    df['ss_previous_chemotherapy'] = df['ss_previous_chemotherapy'].astype('bool')
    df['th_previous_chemotherapy'] = df['ss_previous_chemotherapy'].astype('bool')

    # Entferne Spalten ohne Kürzel -> Entferne noch nicht bearbeitete Zeilen
    df.query("Kuerzel != ''", inplace=True)

    if parameters.get("Mode"):
        global Mode
        if parameters['Mode'] == "additiv":
            print("mode = additiv")

            Mode = True
        if parameters['Mode'] == "subtraktiv":
            Mode = False
            print("mode = subtraktiv")

    global df_AND
    df_AND = df

    def sort_df(string):
        if Mode:
            global df_AND
            df_AND = df_AND.query(string)
        if not Mode:
            print("hier OR")
            global df_or
            temp_df = df.query(string)
            df_or = pandas.concat([df_or, temp_df]).drop_duplicates()  # .reset_index(drop=True)

    # Beginn des Filterns

    # Check für SAPID

    if parameters.get('pat_id_check', None) and parameters["pat_id"]:
        print(type(parameters["pat_id"]))
        global pat_id
        pat_id = int(parameters['pat_id'])
        # df.query("pat_id == @pat_id", inplace= True)
        sort_df("pat_id == @pat_id")

    # Check for Geburtsdatum
    if parameters.get('geburtcheck', None):
        if parameters['von_geburt']:
            global von_geburt
            von_geburt = datetime.datetime.strptime(parameters['von_geburt'], constants.DATEFORMAT)
            von_geburt = datetime.date(von_geburt.year, von_geburt.month, von_geburt.day)
            print(von_geburt)
            # df.query("dob >= @von_geburt",inplace=True)
            sort_df("dob >= @von_geburt")
        if parameters["bis_geburt"]:
            global bis_geburt
            bis_geburt = datetime.datetime.strptime(parameters['bis_geburt'], constants.DATEFORMAT)
            bis_geburt = datetime.date(bis_geburt.year, bis_geburt.month, bis_geburt.day)
            # df.query("dob <= @bis_geburt",inplace=True)
            sort_df("dob <= @bis_geburt")

    # Check for Sex
    if parameters.get('sexcheck', None):
        global sexlist
        sexlist = []
        if parameters.get('männlichcheck', None):
            sexlist.append('m')
            print("Männlich")
        if parameters.get('weiblichcheck', None):
            sexlist.append('f')
            print("weiblich")
        if parameters.get('diverscheck', None):
            sexlist.append('d')
            print("Divers")
        sort_df("sex in @sexlist")

    # Check for Diagnose Codes
    if parameters.get("diagnose_code_check", None):
        if parameters['diagnosis1']:
            print(type(parameters['diagnosis1']))
            # df.query("diagnosis1 == @parameters['diagnosis1']",inplace=True)
            sort_df("diagnosis1 == @parameters['diagnosis1']")
            print("checked for diagnosis1")
        if parameters["diagnosis2"]:
            # df.query("diagnosis2 == @parameters['diagnosis2']",inplace=True)
            sort_df("diagnosis2 == @parameters['diagnosis2']")
            print("checked for diagnosis2")

    # Check for Diagnosis Date
    if parameters.get("diagnosis_date_check", None):
        if parameters['von_diagnosis_date']:
            global von_diagnosis_date
            von_diagnosis_date = datetime.datetime.strptime(parameters['von_diagnosis_date'], constants.DATEFORMAT)
            von_diagnosis_date = datetime.date(von_diagnosis_date.year, von_diagnosis_date.month,
                                               von_diagnosis_date.day)
            # df.query("diagnosis_date >= @von_diagnosis_date",inplace=True)
            sort_df("diagnosis_date >= @von_diagnosis_date")
        if parameters["bis_diagnosis_date"]:
            global bis_diagnosis_date
            bis_diagnosis_date = datetime.datetime.strptime(parameters['bis_diagnosis_date'], constants.DATEFORMAT)
            bis_diagnosis_date = datetime.date(bis_diagnosis_date.year, bis_diagnosis_date.month,
                                               bis_diagnosis_date.day)
            # df.query("diagnosis_date <= @bis_diagnosis_date",inplace=True)
            sort_df("diagnosis_date <= @bis_diagnosis_date")

    # Check for Primary Location
    if parameters.get('primary_location_check', None):
        global locations
        locations = []
        if parameters.get('Rektum_check', None): locations.append('Rektum')
        if parameters.get('Sigma_check', None): locations.append('Sigma')
        if parameters.get('Descendens_check', None): locations.append('Descendens')
        if parameters.get('Transversum_check', None): locations.append('Transversum')
        if parameters.get('Ascendens_check', None): locations.append('Ascendens')
        if parameters.get('Zäkum_check', None): locations.append('Zäkum')
        if parameters.get('Rektosigmoid_check', None): locations.append('Rektosigmoid')
        # df.query("primary_location in @locations", inplace=True)
        sort_df("primary_location in @locations")

    # Check for Synchron/Metachron
    if parameters.get('crlm_met_syn_check', None):
        global crlm_list
        crlm_list = []
        if parameters.get('Synchron_check', None): crlm_list.append('synchron');print("synchron")
        if parameters.get('Metachron_check', None): crlm_list.append('metachron');print("metachron")
        # df.query("crlm_met_syn in @crlm_list", inplace=True)
        sort_df("crlm_met_syn in @crlm_list")

    # check for Bilobulär#
    if parameters.get('Bilobulär_check', None):
        if parameters.get('bilobulär_check_yes', None):
            # df.query("crlm_bilobular == 1", inplace = True)
            sort_df("crlm_bilobular == 1")
        if parameters.get('bilobulär_check_no', None):
            # df.query("crlm_bilobular == 0", inplace = True)
            sort_df("crlm_bilobular == 0")
        print("inside bilobulär")

    # Check for Multimodal

    if parameters.get('multimodal_check', None):
        if parameters.get('multimodal_check_yes', None):
            # df.query("multimodal == 1", inplace = True)
            sort_df("multimodal == 1")
        if parameters.get('multimodal_check_no', None):
            # df.query("multimodal == 0", inplace = True)
            sort_df("multimodal == 0")

    # Check for twostaged
    if parameters.get('twostaged_check', None):
        if parameters.get('twostaged_check_yes', None):
            # df.query("two_staged == 1", inplace = True)
            sort_df("two_staged==1")
        if parameters.get('twostaged_check_no', None):
            # df.query("two_staged == 0", inplace = True)
            sort_df("two_staged==0")

    # Check for BRAF
    if parameters.get('braf_check', None):
        global braf
        braf = []
        if parameters.get('braf_mutiert_check', None): braf.append('mut')
        if parameters.get('braf_wildtyp_check', None): braf.append('wt')
        # df.query("BRAF in @braf", inplace=True)
        sort_df("BRAF in @braf")

    # Check for RAS
    if parameters.get('ras_check', None):
        global ras
        ras = []
        if parameters.get('ras_mutiert_check', None): ras.append('mut')
        if parameters.get('ras_wildtyp_check', None): ras.append('wt')
        # df.query("RAS in @ras", inplace=True)
        sort_df("RAS in @ras")

    # Check for MSS
    if parameters.get('mss_check', None):
        global mss
        mss = []
        if parameters.get('mss', None): mss.append('mss')
        if parameters.get('msi', None): mss.append('msi')
        # df.query("MSS in @mss", inplace=True)
        sort_df("MSS in @mss")
    # Check for T
    if parameters.get('t_check', None) and parameters["T"]:
        para = parameters['T']
        # df.query("T == @para", inplace= True)
        sort_df("T == @para")

    # Check for N
    if parameters.get('n_check', None) and parameters["N"]:
        para = parameters['N']
        # df.query("N == @para", inplace= True)
        sort_df("N == @para")

    # Check for M
    if parameters.get('m_check', None) and parameters["M"]:
        para = parameters['M']
        # df.query("M == @para", inplace= True)
        sort_df("M==@para")
    # Check for LK
    if parameters.get('lk_check', None) and parameters["LK"]:
        #para = int(parameters['LK'])
        # df.query("LK == @para", inplace= True)
        sort_df("LK == @para")
        # Check for L
    if parameters.get('l_check', None) and parameters["L"]:
        para = int(parameters['L'])
        # df.query("L == @para", inplace= True)
        sort_df("L == @para")

    # Check for V
    if parameters.get('v_check', None) and parameters["V"]:
        para = int(parameters['V'])
        # df.query("V == @para", inplace= True)
        sort_df("V == @para")
    # Check for R
    if parameters.get('r_check', None) and parameters["R"]:
        para = int(parameters['R'])
        # df.query("R == @para", inplace= True)
        sort_df("R == @para")

    # Check for G
    if parameters.get('g_check', None) and parameters["G"]:
        para = int(parameters['G'])
        # df.query("G == @para", inplace= True)
        sort_df("G==@para")

    # Check for Last Seen Date
    if parameters.get("last_seen_check", None):
        if parameters['date_fu_von']:
            global date_fu_von
            date_fu_von = datetime.datetime.strptime(parameters['date_fu_von'], constants.DATEFORMAT)
            date_fu_von = datetime.date(date_fu_von.year, date_fu_von.month, date_fu_von.day)
            # df.query("date_fu >= @date_fu_von",inplace=True)
            sort_df("date_fu >= @date_fu_von")
        if parameters["date_fu_bis"]:
            global date_fu_bis
            date_fu_bis = datetime.datetime.strptime(parameters['date_fu_bis'], constants.DATEFORMAT)
            date_fu_bis = datetime.date(date_fu_bis.year, date_fu_bis.month, date_fu_bis.day)
            # df.query("date_fu <= @date_fu_bis",inplace=True)
            sort_df("date_fu <= @date_fu_bis")

    # Check for Alive or Not
    if parameters.get("died_check", None):
        if parameters.get("died_no_check", None):
            # df.query("status_fu == 0",inplace=True)
            sort_df("status_fu == 0")
        if parameters.get("died_yes_check", None):
            # df.query("status_fu == 1",inplace=True)
            sort_df("status_fu == 1")

    # Check for Rezidiv
    if parameters.get("rezidiv_check", None):
        if parameters.get("rezidiv_check_no", None):
            # df.query("recurrence_status == 0",inplace=True)
            sort_df("recurrence_status == 0")
        if parameters.get("rezidiv_check_yes", None):
            # df.query("recurrence_status == 1",inplace=True)
            sort_df("recurrence_status == 1")
    # Check for ASA
    if parameters.get("asa_check", None):
        if parameters.get("asa_check_not_found", None):
            # df.query("asa == 0",inplace=True)
            sort_df("asa== 0")
        if parameters.get("asa_check_1", None):
            # df.query("asa == 1",inplace=True)
            sort_df("asa== 1")
        if parameters.get("asa_check_2", None):
            # df.query("asa == 2",inplace=True)
            sort_df("asa== 2")
        if parameters.get("asa_check_3", None):
            # df.query("asa == 3",inplace=True)
            sort_df("asa== 3")
        if parameters.get("asa_check_4", None):
            # df.query("asa == 4",inplace=True)
            sort_df("asa== 4")
        if parameters.get("asa_check_5", None):
            sort_df("asa== 5")
            # df.query("asa == 5",inplace=True)

    # Check for BMI
    if parameters.get("bmi_check", None):
        if parameters["von_bmi_input"]:
            # df.query("bmi == @parameters['von_bmi_input']", inpacte=True)
            sort_df("bmi == @parameters['von_bmi_input']")
        if parameters["bis_bmi_input"]:
            # df.query("bmi == @parameters['bis_bmi_input']", inplace=True)
            sort_df("bmi == @parameters['von_bmi_input']")

    # Check for alc
    if parameters.get("alc_check", None):
        if parameters.get("yes_alcohol_check", None):
            # df.query("alcohol == 0",inplace=True)
            sort_df("alcohol == 0")
        if parameters.get("no_alcohol_check", None):
            # df.query("alcohol == 1",inplace=True)
            sort_df("alcohol == 1")

    # Check for Raucher
    if parameters.get("smoking_check", None):
        if parameters.get("smoking_check_yes", None):
            # df.query("smoking  == 0",inplace=True)
            sort_df("smoking == 0")
        if parameters.get("smoking_check_no", None):
            # df.query("smoking  == 1",inplace=True)
            sort_df("smoking == 1")

    # Check for Diabetiker
    if parameters.get("diabetes_check", None):
        if parameters.get("diabetes_check_yes", None):
            # df.query("diabetes  == 0",inplace=True)
            sort_df("diabetes  == 0")
        if parameters.get("diabetes_check_no", None):
            # df.query("diabetes  == 1",inplace=True)
            sort_df("diabetes  == 1")

    # Check for Zirrose
    if parameters.get("zirrose_check", None):
        if parameters.get("zirrose_check_yes", None):
            # df.query("cirrhosis   == 0",inplace=True)
            sort_df("cirrhosis   == 0")

        if parameters.get("zirrose_check_no", None):
            # df.query("cirrhosis   == 1",inplace=True)
            sort_df("cirrhosis   == 1")

    # Check for Fibrose
    if parameters.get("fibrose_check", None):
        if parameters.get("fibrose_check_yes", None):
            # df.query("fibrosis == 0",inplace=True)
            sort_df("fibrosis == 0")
        if parameters.get("fibrose_check_no", None):
            # df.query("fibrosis == 1",inplace=True)
            sort_df("fibrosis == 1")

    # Check for Previous OPs
    if parameters.get("PreviousOPs", None):
        if parameters["previous_surgery_code"]:
            # df.query("previous_surgery == @parameters('previous_surgery_code')",inplace=True)
            sort_df("previous_surgery == @parameters('previous_surgery_code')")
        if parameters['previous_surgery_date_von']:
            von_date = datetime.datetime.strptime(parameters['previous_surgery_date_von'], constants.DATEFORMAT)
            von_date = datetime.date(von_date.year, von_date.month, von_date.day)
            # df.query("previous_surgery >= @von_date",inplace=True)
            sort_df("previous_surgery >= @von_date")
        if parameters['previous_surgery_date_bis']:
            bis_date = datetime.datetime.strptime(parameters['previous_surgery_date_bis'], constants.DATEFORMAT)
            bis_date = datetime.date(bis_date.year, bis_date.month, bis_date.day)
            # df.query("previous_surgery <= @bis_date",inplace=True)
            sort_df("previous_surgery <= @bis_date")

    # Check for FS_Chemo
    if parameters.get("fs_previous_chemotherapy", None):
        if parameters.get("fs_chemo_check_no", None):
            if Mode:
                df_AND = df_AND[df_AND['op_date_Surgery1'].notnull()]
            # df.query("fs_previous_chemotherapy == 0", inplace=True)
            sort_df("fs_previous_chemotherapy == 0")
        if parameters["fs_previous_chemotherapy_cycles_von"]:
            para = int(parameters['fs_previous_chemotherapy_cycles_von'])
            # df.query("fs_previous_chemotherapy_cycles == @para", inplace= True)
            sort_df("fs_previous_chemotherapy_cycles >= @para")
        if parameters["fs_previous_chemotherapy_cycles_bis"]:
            para = int(parameters['fs_previous_chemotherapy_cycles_bis'])
            # df.query("fs_previous_chemotherapy_cycles == @para", inplace= True)
            sort_df("fs_previous_chemotherapy_cycles <= @para")
        if parameters["fs_previous_chemotherapy_type"]:
            # df.query("fs_previous_chemotherapy_type = @parameters['fs_previous_chemotherapy_typ']",inplace=True)
            sort_df("fs_previous_chemotherapy_type = @parameters['fs_previous_chemotherapy_typ']")
        if parameters["fs_previous_antibody"]:
            # df.query("fs_previous_antibody = @parameters['fs_previous_antibody']",inplace=True)
            sort_df("fs_previous_antibody = @parameters['fs_previous_antibody']")

    # Check for SS_Chemo
    if parameters.get("ss_previous_chemotherapy", None):
        if parameters.get("ss_chemo_check_no", None):
            if Mode:
                df_AND = df_AND[df_AND['op_date_Surgery2'].notnull()]

            # df.query("ss_previous_chemotherapy == 0", inplace=True)
            sort_df("ss_previous_chemotherapy == 0")
        if parameters["ss_previous_chemotherapy_cycles_von"]:
            para = int(parameters['ss_previous_chemotherapy_cycles_von'])
            # df.query("ss_previous_chemotherapy_cycles == @para", inplace= True)
            sort_df("ss_previous_chemotherapy_cycles == @para")
        if parameters["ss_previous_chemotherapy_cycles_bis"]:
            para = int(parameters['ss_previous_chemotherapy_cycles_bis'])
            # df.query("ss_previous_chemotherapy_cycles == @para", inplace= True)
            sort_df("ss_previous_chemotherapy_cycles == @para")
        if parameters["ss_previous_chemotherapy_type"]:
            # df.query("ss_previous_chemotherapy_type = @parameters['ss_previous_chemotherapy_typ']",inplace=True)
            sort_df("ss_previous_chemotherapy_cycles == @para")
        if parameters["ss_previous_antibody"]:
            # df.query("ss_previous_antibody = @parameters['ss_previous_antibody']",inplace=True)
            sort_df("ss_previous_antibody = @parameters['ss_previous_antibody']")

    # Check for TH_Chemo
    if parameters.get("th_previous_chemotherapy", None):
        if parameters.get("th_chemo_check_no", None):
            if Mode:
                df_AND = df_AND[df_AND['op_date_Surgery23'].notnull()]
            # df.query("th_previous_chemotherapy == 0", inplace=True)
            sort_df("th_previous_chemotherapy == 0")

        if parameters["th_previous_chemotherapy_cycles_von"]:
            para = int(parameters['th_previous_chemotherapy_cycles_von'])
            # df.query("th_previous_chemotherapy_cycles == @para", inplace= True)
            sort_df("th_previous_chemotherapy_cycles == @para")
        if parameters["th_previous_chemotherapy_cycles_bis"]:
            para = int(parameters['th_previous_chemotherapy_cycles_bis'])
            # df.query("th_previous_chemotherapy_cycles == @para", inplace= True)
            sort_df("th_previous_chemotherapy_cycles == @para")
        if parameters["th_previous_chemotherapy_type"]:
            # df.query("th_previous_chemotherapy_type = @parameters['th_previous_chemotherapy_typ']",inplace=True)
            sort_df("th_previous_chemotherapy_type = @parameters['th_previous_chemotherapy_typ']")
        if parameters["th_previous_antibody"]:
            # df.query("th_previous_antibody = @parameters['th_previous_antibody']",inplace=True)
            sort_df("th_previous_antibody = @parameters['th_previous_antibody']")

    # Check for PVE
    if parameters.get("PVECheck", None):
        print("pvecheck true")
        if parameters.get("PVE_check_yes", None):
            print("checking for PVE = 1")
            # df.query("pve == 1", inplace=True)
            sort_df("pve == 1")
        if parameters.get("PVE_check_no", None):
            print("checking for PVE = 0")
            # df.query("pve == 0", inplace=True)
            sort_df("pve == 0")

    # Check for First OPs 

    if parameters.get("FirstOP_Check", None):
        if Mode:
            df_AND = df_AND[df_AND['op_date_Surgery1'].notnull()]
        # df.query("op_date_Surgery1 != ''", inplace=True)
        sort_df("op_date_Surgery1 != ''")
        # df.query("op_date_Surgery2 == ''", inplace=True)
        sort_df("op_date_Surgery2 == ''")
        # df.query("op_date_Surgery3 == ''", inplace=True)
        sort_df("op_date_Surgery3 == ''")
        print("in OP1")
    # Check for Second Ops
    if parameters.get("secondOP_Check", None):
        if Mode:
            df_AND = df_AND[df_AND['op_date_Surgery2'].notnull()]
        # df.query("op_date_Surgery2 != ''", inplace=True)
        sort_df("op_date_Surgery2 != ''")
        print("in OP2")
    # Check for First Ops
    if parameters.get("thirdOP_Check", None):
        if Mode:
            df_AND = df_AND[df_AND['op_date_Surgery3'].notnull()]
        # df.query("op_date_Surgery3 != ''", inplace=True)
        sort_df("op_date_Surgery3 != ''")

    # Check for Limax Initial + Date
    if parameters.get("limax_initial_von", None):
        para = int(parameters['limax_initial_von'])
        # df.query("limax_initial >= @para", inplace=True)
        sort_df("limax_initial >= @para")
    if parameters.get("limax_initial_bis", None):
        para = int(parameters['limax_initial_bis'])
        # df.query("limax_initial <= @para", inplace=True)
        sort_df("limax_initial <= @para")
    if parameters.get('limax_initial_date_von', None):
        von_date = datetime.datetime.strptime(parameters['limax_initial_date_von'], constants.DATEFORMAT)
        von_date = datetime.date(von_date.year, von_date.month, von_date.day)
        print(von_geburt)
        # df.query("limax_initial_date >= @von_date",inplace=True)
        sort_df("limax_initial_date >= @von_date")
    if parameters.get('limax_initial_date_bis', None):
        bis_date = datetime.datetime.strptime(parameters['limax_initial_date_bis'], constants.DATEFORMAT)
        bis_date = datetime.date(bis_date.year, bis_date.month, bis_date.day)
        print(von_geburt)
        # df.query("limax_initial_date <= @bis_date",inplace=True)
        sort_df("limax_initial_date <= @bis_date")

    # Check for Limax Second + Date

    if parameters.get("limax_second_von", None):
        para = int(parameters['limax_second_von'])
        # df.query("limax_second >= @para", inplace=True)
        sort_df("limax_second >= @para")
    if parameters.get("limax_second_bis", None):
        para = int(parameters['limax_second_bis'])
        # df.query("limax_second <= @para", inplace=True)
        sort_df("limax_second <= @para")
    if parameters.get('limax_second_date_von', None):
        von_date = datetime.datetime.strptime(parameters['limax_second_date_von'], constants.DATEFORMAT)
        von_date = datetime.date(von_date.year, von_date.month, von_date.day)
        print(von_geburt)
        # df.query("limax_second_date >= @von_date",inplace=True)
        sort_df("limax_second_date >= @von_date")
    if parameters.get('limax_second_date_bis', None):
        bis_date = datetime.datetime.strptime(parameters['limax_second_date_bis'], constants.DATEFORMAT)
        bis_date = datetime.date(bis_date.year, bis_date.month, bis_date.day)
        print(von_geburt)
        sort_df("limax_second_date <= @bis_date")
        # df.query("limax_second_date <= @bis_date",inplace=True)

    # Check for Limax Third + Date

    if parameters.get("limax_third_von", None):
        para = int(parameters['limax_third_von'])
        # df.query("limax_third >= @para", inplace=True)
        sort_df("limax_third >= @para")
    if parameters.get("limax_third_bis", None):
        para = int(parameters['limax_third_bis'])
        # df.query("limax_third <= @para", inplace=True)
        sort_df("limax_third <= @para")
    if parameters.get('limax_third_date_von', None):
        von_date = datetime.datetime.strptime(parameters['limax_third_date_von'], constants.DATEFORMAT)
        von_date = datetime.date(von_date.year, von_date.month, von_date.day)
        print(von_geburt)
        # df.query("limax_third_date >= @von_date",inplace=True)
        sort_df("limax_third_date >= @von_date")
    if parameters.get('limax_third_date_bis', None):
        bis_date = datetime.datetime.strptime(parameters['limax_third_date_bis'], constants.DATEFORMAT)
        bis_date = datetime.date(bis_date.year, bis_date.month, bis_date.day)
        print(von_geburt)
        # df.query("limax_third_date <= @bis_date",inplace=True)
        sort_date("limax_third_date <= @bis_date")

    # Check for First OP Parameters Date

    if parameters.get("Fs_op_date", None):
        if parameters.get('op_date_Surgery1_von', None):
            von_date = datetime.datetime.strptime(parameters['op_date_Surgery1_von'], constants.DATEFORMAT)
            von_date = datetime.date(von_date.year, von_date.month, von_date.day)
            print(von_geburt)
            # df.query("op_date_Surgery1 >= @von_date",inplace=True)
            sort_df("op_date_Surgery1 >= @von_date")
        if parameters.get('op_date_Surgery1', None):
            bis_date = datetime.datetime.strptime(parameters['limax_third_date_bis'], constants.DATEFORMAT)
            bis_date = datetime.date(bis_date.year, bis_date.month, bis_date.day)
            print(von_geburt)
            # df.query("op_date_Surgery1 <= @bis_date",inplace=True)
            sort_df("op_date_Surgery1 <= @bis_date")

    # Check for First Op Code
    if parameters.get("op_code_Surgery1_checkbox", None):
        if parameters['op_code_Surgery1']:
            print(type(parameters['op_code_Surgery1']))
            # df.query("op_code_Surgery1 == @parameters['op_code_Surgery1']",inplace=True)
            sort_df("op_code_Surgery1 == @parameters['op_code_Surgery1']")

    # Check for First OP Diagnosis
    if parameters.get("op_diagnosis_Surgery1_checkbox", None):
        if parameters['op_diagnosis_Surgery1']:
            print(type(parameters['op_diagnosis_Surgery1']))
            # df.query("op_diagnosis_Surgery1 == @parameters['op_diagnosis_Surgery1']",inplace=True)
            sort_df("op_diagnosis_Surgery1 == @parameters['op_diagnosis_Surgery1']")
    print(parameters)

    # Check for OP Methode
    if parameters.get('op_method_checkbox', None):
        paralist = []
        if parameters.get('checkoffen', None): paralist.append('offen'); print("offen")
        if parameters.get('checklaparoskopisch', None): paralist.append('laparoskopisch');print("laparoskopisch")
        if parameters.get('checkrobo', None): paralist.append('robotisch');print("checkrobo")
        # df.query("first_surgery_minimal_invasive in @paralist", inplace=True)
        sort_df("first_surgery_minimal_invasive in @paralist")

    # Check for OP Konversion
    if parameters.get('op_occurence_checkbox', None):
        if parameters['op1_conversion_check']:
            # df.query("first_surgery_conversion == 1",inplace=True)
            sort_df("first_surgery_conversion == 1")
        if parameters['op1_ablation_check']:
            # df.query("first_surgery == 1",inplace=True)
            sort_df("first_surgery_ablation == 1")

    # Check for Length
    if parameters.get("op_length_checkbox", None):
        if parameters["op_length_von"]:
            para = int(parameters['op_length_von'])
            # df.query("first_surgery_length >= @para", inplace=True)
            sort_df("first_surgery_length >= @para")
        if parameters["op_length_bis"]:
            para = int(parameters['op_length_bis'])
            # df.query("first_surgery_length <= @para", inplace=True)
            sort_df("first_surgery_length <= @para")

    # Check for INtensivzeit
    if parameters.get("icu_checkbox", None):
        print("in ICU")
        if parameters["icu_von"]:
            print("tried to filter >")

            para = int(parameters['icu_von'])
            # df.query("fs_icu >= @para", inplace=True)
            sort_df("fs_icu >= @para")
        if parameters["icu_bis"]:
            print("tried to filter <")

            para = int(parameters['fs_icu_bis'])
            # df.query("fs_icu <= @para", inplace=True)
            sort_df("fs_icu <= @para")

    #  Check for LOS
    if parameters.get("fs_los_checkbox", None):
        if parameters["fs_los_von"]:
            para = int(parameters['fs_los_von'])
            # df.query("fs_los >= @para", inplace=True)
            sort_df("fs_los >= @para")
        if parameters["fs_los_bis"]:
            para = int(parameters['fs_los_bis'])
            # df.query("fs_los <= @para", inplace=True)
            sort_df("fs_los <= @para")

    # Check for DINDO
    if parameters.get('fs_dindo_checkbox', None):
        paralist = []
        if parameters.get('fs_check_dindo_0', None):
            paralist.append('No comp')
            paralist.append('No comp')
            print("No Complications")
        if parameters.get('fs_check_dindo_1', None):
            paralist.append('I')
            print("I")
        if parameters.get('fs_check_dindo_2', None):
            paralist.append('II')
            print("II")
        if parameters.get('fs_check_dindo_3a', None):
            paralist.append('IIIa')
            print("IIIa")
        if parameters.get('fs_check_dindo_3b', None):
            paralist.append('IIIb')
            print("IIIb")
        if parameters.get('fs_check_dindo_4a', None):
            paralist.append('IVa')
            print("IVa")
        if parameters.get('fs_check_dindo_4b', None):
            paralist.append('IVb')
            print("IVb")
        if parameters.get('fs_check_dindo_5', None):
            paralist.append('V')
            print("V")
        print(paralist)
        # df.query("fs_dindo in @paralist", inplace=True)
        sort_df("fs_dindo in @paralist")

    # Check for Laborparameters first OP

    # #check for SerumBili fs

    # # Check for POD1
    if parameters.get("fs_serum_bili_pod1_checkbox", None):
        if parameters["fs_Serum_Bili_POD1_von"]:
            para = int(parameters['fs_Serum_Bili_POD1_von'])
            # df.query("fs_Serum_Bili_POD1 >= @para", inplace= True)
            sort_df("fs_Serum_Bili_POD1 >= @para")
        if parameters["fs_Serum_Bili_POD1_bis"]:
            para = int(parameters['fs_Serum_Bili_POD1_bis'])
            # df.query("fs_Serum_Bili_POD1 <= @para", inplace= True)
            sort_df("fs_Serum_Bili_POD1 <= @para")

    # # Check for POD3
    if parameters.get("fs_serum_bili_pod3_checkbox", None):
        if parameters["fs_Serum_Bili_POD3_von"]:
            para = int(parameters['fs_Serum_Bili_POD3_von'])
            # df.query("fs_Serum_Bili_POD3 >= @para", inplace= True)
            sort_df("fs_Serum_Bili_POD3 >= @para")
        if parameters["fs_Serum_Bili_POD3_bis"]:
            para = int(parameters['fs_Serum_Bili_POD3_bis'])
            # df.query("fs_Serum_Bili_POD3 <= @para", inplace= True)
            sort_df("fs_Serum_Bili_POD3 <= @para")

    # # Check for POD5
    if parameters.get("fs_serum_bili_pod5_checkbox", None):
        if parameters["fs_Serum_Bili_POD5_von"]:
            para = int(parameters['fs_Serum_Bili_POD5_von'])
            # df.query("fs_Serum_Bili_POD5 >= @para", inplace= True)
            sort_df("fs_Serum_Bili_POD5 >= @para")
        if parameters["fs_Serum_Bili_POD5_bis"]:
            para = int(parameters['fs_Serum_Bili_POD5_bis'])
            # df.query("fs_Serum_Bili_POD5 <= @para", inplace= True)
            sort_df("fs_Serum_Bili_POD5 <= @para")

    # # Check for Last
    if parameters.get("fs_serum_bili_last_checkbox", None):
        if parameters["fs_Serum_Bili_last_von"]:
            para = int(parameters['fs_Serum_Bili_last_von'])
            # df.query("fs_Serum_Bili_Last >= @para", inplace= True)
            sort_df("fs_Serum_Bili_Last >= @para")
        if parameters["fs_Serum_Bili_last_bis"]:
            para = int(parameters['fs_Serum_Bili_last_bis'])
            # df.query("fs_Serum_Bili_Last <= @para", inplace= True)
            sort_df("fs_Serum_Bili_Last <= @para")

    # #check for Drain Bili fs

    # # Check for POD1
    if parameters.get("fs_drain_bili_pod1_checkbox", None):
        if parameters["fs_drain_Bili_pod1_von"]:
            para = int(parameters['fs_drain_Bili_pod1_von'])
            # df.query("fs_Drain_Bili_POD1 >= @para", inplace= True)
            sort_df("fs_Drain_Bili_POD1 >= @para")
        if parameters["fs_drain_Bili_pod1_bis"]:
            para = int(parameters['fs_drain_Bili_pod1_bis'])
            # df.query("fs_Drain_Bili_POD1 <= @para", inplace= True)
            sort_df("fs_Drain_Bili_POD1 <= @para")

    # # Check for POD3
    if parameters.get("fs_drain_bili_pod3_checkbox", None):
        if parameters["fs_drain_Bili_pod3_von"]:
            para = int(parameters['fs_drain_Bili_pod3_von'])
            # df.query("fs_Drain_Bili_POD3 >= @para", inplace= True)
            sort_df("fs_Drain_Bili_POD3 >= @para")
        if parameters["fs_drain_Bili_pod3_bis"]:
            para = int(parameters['fs_drain_Bili_pod3_bis'])
            # df.query("fs_Drain_Bili_POD3 <= @para", inplace= True)
            sort_df("fs_Drain_Bili_POD3 <= @para")

    # # Check for POD5
    if parameters.get("fs_drain_bili_pod5_checkbox", None):
        if parameters["fs_drain_Bili_pod5_von"]:
            para = int(parameters['fs_drain_Bili_pod5_von'])
            # df.query("fs_Drain_Bili_POD5 >= @para", inplace= True)
            sort_df("fs_Drain_Bili_POD5 >= @para")
        if parameters["fs_drain_Bili_pod5_bis"]:
            para = int(parameters['fs_drain_Bili_pod5_bis'])
            # df.query("fs_Drain_Bili_POD5 <= @para", inplace= True)
            sort_df("fs_Drain_Bili_POD5 <= @para")

    # # Check for Last
    if parameters.get("fs_drain_bili_last_checkbox", None):
        if parameters["fs_drain_Bili_last_von"]:
            para = int(parameters['fs_drain_Bili_last_von'])
            # df.query("fs_Drain_Bili_Last >= @para", inplace= True)
            sort_df("fs_Drain_Bili_Last >= @para")
        if parameters["fs_drain_Bili_last_bis"]:
            para = int(parameters['fs_drain_Bili_last_bis'])
            # df.query("fs_Drain_Bili_Last <= @para", inplace= True)
            sort_para("fs_Drain_Bili_Last <= @para")

    # #Check for AST
    # # Check for POD1
    if parameters.get("fs_AST_pod1_checkbox", None):
        if parameters["fs_AST_pod1_von"]:
            para = int(parameters['fs_AST_pod1_von'])
            # df.query("fs_AST_POD1 >= @para", inplace= True)
            sort_df("fs_AST_POD1 >= @para")
        if parameters["fs_AST_pod1_bis"]:
            para = int(parameters['fs_AST_pod1_bis'])
            # df.query("fs_AST_POD1 <= @para", inplace= True)
            sort_df("fs_AST_POD1 <= @para")

    # # Check for POD3
    if parameters.get("fs_AST_pod3_checkbox", None):
        if parameters["fs_AST_pod3_von"]:
            para = int(parameters['fs_AST_pod3_von'])
            # df.query("fs_AST_POD3 >= @para", inplace= True)
            sort_df("fs_AST_POD3 >= @para")
        if parameters["fs_AST_pod3_bis"]:
            para = int(parameters['fs_AST_pod3_bis'])
            # df.query("fs_AST_POD3 <= @para", inplace= True)
            sort_df("fs_AST_POD3 <= @para")

    # # Check for POD5
    if parameters.get("fs_AST_pod5_checkbox", None):
        if parameters["fs_AST_pod5_von"]:
            para = int(parameters['fs_AST_pod5_von'])
            # df.query("fs_AST_POD5 >= @para", inplace= True)
            sort_df("fs_AST_POD5 >= @para")
        if parameters["fs_AST_pod5_bis"]:
            para = int(parameters['fs_AST_pod5_bis'])
            # df.query("fs_AST_POD5 <= @para", inplace= True)
            sort_df("fs_AST_POD5 <= @para")

    # # Check for Last
    if parameters.get("fs_AST_last_checkbox", None):
        if parameters["fs_AST_last_von"]:
            para = int(parameters['fs_AST_last_von'])
            # df.query("fs_AST_Last >= @para", inplace= True)
            sort_df("fs_AST_Last >= @para")
        if parameters["fs_AST_last_bis"]:
            para = int(parameters['fs_AST_last_bis'])
            # df.query("fs_AST_Last <= @para", inplace= True)
            sort_df("fs_AST_Last <= @para")

    # #Check for ALT fs
    # # Check for POD1
    if parameters.get("fs_ALT_pod1_checkbox", None):
        if parameters["fs_ALT_pod1_von"]:
            para = int(parameters['fs_ALT_pod1_von'])
            # df.query("fs_ALT_POD1 >= @para", inplace= True)
            sort_df("fs_ALT_POD1 >= @para")
        if parameters["fs_ALT_pod1_bis"]:
            para = int(parameters['fs_ALT_pod1_bis'])
            # df.query("fs_ALT_POD1 <= @para", inplace= True)
            sort_df("fs_ALT_POD1 <= @para")

    # # Check for POD3
    if parameters.get("fs_ALT_pod3_checkbox", None):
        if parameters["fs_ALT_pod3_von"]:
            para = int(parameters['fs_ALT_pod3_von'])
            # df.query("fs_ALT_POD3 >= @para", inplace= True)
            sort_df("fs_ALT_POD3 >= @para")
        if parameters["fs_ALT_pod3_bis"]:
            para = int(parameters['fs_ALT_pod3_bis'])
            # df.query("fs_ALT_POD3 <= @para", inplace= True)
            sort_df("fs_ALT_POD3 <= @para")

    # # Check for POD5
    if parameters.get("fs_ALT_pod5_checkbox", None):
        if parameters["fs_ALT_pod5_von"]:
            para = int(parameters['fs_ALT_pod5_von'])
            # df.query("fs_ALT_POD5 >= @para", inplace= True)
            sort_df("fs_ALT_POD5 >= @para")
        if parameters["fs_ALT_pod5_bis"]:
            para = int(parameters['fs_ALT_pod5_bis'])
            # df.query("fs_ALT_POD5 <= @para", inplace= True)
            sort_df("fs_ALT_POD5 <= @para")

    # # Check for Last
    if parameters.get("fs_ALT_Last_checkbox", None):
        if parameters["fs_ALT_Last_von"]:
            para = int(parameters['fs_ALT_Last_von'])
            # df.query("fs_ALT_Last >= @para", inplace= True)
            sort_df("fs_ALT_Last >= @para")
        if parameters["fs_ALT_Last_bis"]:
            para = int(parameters['fs_ALT_Last_bis'])
            # df.query("fs_ALT_Last <= @para", inplace= True)
            sort_df("fs_ALT_Last <= @para")

    # #Check for INR
    if parameters.get("fs_INR_pod1_checkbox", None):
        if parameters["fs_INR_pod1_von"]:
            para = int(parameters['fs_INR_pod1_von'])
            # df.query("fs_INR_POD1 >= @para", inplace= True)
            sort_df("fs_INR_POD1 >= @para")
        if parameters["fs_INR_pod1_bis"]:
            para = int(parameters['fs_INR_pod1_bis'])
            # df.query("fs_INR_POD1 <= @para", inplace= True)
            sort_df("fs_INR_POD1 <= @para")

    # # Check for POD3
    if parameters.get("fs_INR_pod3_checkbox", None):
        if parameters["fs_INR_pod3_von"]:
            para = int(parameters['fs_INR_pod3_von'])
            # df.query("fs_INR_POD3 >= @para", inplace= True)
            sort_df("fs_INR_POD3 >= @para")
        if parameters["fs_INR_pod3_bis"]:
            para = int(parameters['fs_INR_pod3_bis'])
            # df.query("fs_INR_POD3 <= @para", inplace= True)
            sort_df("fs_INR_POD3 <= @para")

    # # Check for POD5
    if parameters.get("fs_INR_pod5_checkbox", None):
        if parameters["fs_INR_pod5_von"]:
            para = int(parameters['fs_INR_pod5_von'])
            # df.query("fs_INR_POD5 >= @para", inplace= True)
            sort_df("fs_INR_POD5 >= @para")
        if parameters["fs_INR_pod5_bis"]:
            para = int(parameters['fs_INR_pod5_bis'])
            # df.query("fs_INR_POD5 <= @para", inplace= True)
            sort_df("fs_INR_POD5 <= @para")

    # # Check for Last
    if parameters.get("fs_INR_Last_checkbox", None):
        if parameters["fs_INR_Last_von"]:
            para = int(parameters['fs_INR_Last_von'])
            # df.query("fs_INR_Last >= @para", inplace= True)
            sort_df("fs_INR_Last >= @para")
        if parameters["fs_INR_Last_bis"]:
            para = int(parameters['fs_INR_Last_bis'])
            # df.query("fs_INR_Last <= @para", inplace= True)
            sort_df("fs_INR_Last <= @para")

    # Second OP Data
    if parameters.get("ss_op_date", None):
        if parameters.get('op_date_Surgery2_von', None):
            von_date = datetime.datetime.strptime(parameters['op_date_Surgery2_von'], constants.DATEFORMAT)
            von_date = datetime.date(von_date.year, von_date.month, von_date.day)
            print(von_geburt)
            # df.query("op_date_Surgery2 >= @von_date",inplace=True)
            sort_df("op_date_Surgery2 >= @von_date")
        if parameters.get('op_date_Surgery2', None):
            bis_date = datetime.datetime.strptime(parameters['limax_third_date_bis'], constants.DATEFORMAT)
            bis_date = datetime.date(bis_date.year, bis_date.month, bis_date.day)
            print(von_geburt)
            # df.query("op_date_Surgery2 <= @bis_date",inplace=True)
            sort_df("op_date_Surgery2 <= @bis_date")

    # Check for Second Op Code
    if parameters.get("op_code_Surgery2_checkbox", None):
        if parameters['op_code_Surgery2']:
            print(type(parameters['op_code_Surgery2']))
            # df.query("op_code_Surgery2 == @parameters['op_code_Surgery2']",inplace=True)
            sort_df("op_code_Surgery2 == @parameters['op_code_Surgery2']")

    # Check for Second OP Diagnosis
    if parameters.get("op_diagnosis_Surgery2_checkbox", None):
        if parameters['op_diagnosis_Surgery2']:
            print(type(parameters['op_diagnosis_Surgery2']))
            # df.query("op_diagnosis_Surgery2 == @parameters['op_diagnosis_Surgery2']",inplace=True)
            sort_df("op_diagnosis_Surgery2 == @parameters['op_diagnosis_Surgery2']")

    print(parameters)

    # Check for OP Methode
    if parameters.get('ss_op_method_checkbox', None):

        paralist = []
        if parameters.get('ss_checkoffen', None): paralist.append('offen'); print("offen")
        if parameters.get('ss_checklaparoskopisch', None): paralist.append('laparoskopisch');print("laparoskopisch")
        if parameters.get('ss_checkrobo', None): paralist.append('robotisch');print("checkrobo")
        # df.query("second_surgery_minimal_invasive in @paralist", inplace=True)
        sort_df("second_surgery_minimal_invasive in @paralist")

    # Check for OP Konversion
    if parameters.get('ss_op_occurence_checkbox', None):
        if parameters['op2_conversion_check']:
            # df.query("second_surgery_conversion == 1",inplace=True)
            sort_df("second_surgery_conversion == 1")
        if parameters['op2_ablation_check']:
            # df.query("second_surgery_ablation == 1",inplace=True)
            sort_df("second_surgery_ablation == 1")

    # Check for Length
    if parameters.get("ss_op_length_checkbox", None):
        if parameters["op_length_von"]:
            para = int(parameters['op_length_von'])
            # df.query("second_surgery_length >= @para", inplace=True)
            sort_df("second_surgery_length >= @para")
        if parameters["ss_op_length_bis"]:
            para = int(parameters['op_length_bis'])
            # df.query("second_surgery_length <= @para", inplace=True)
            sort_df("second_surgery_length <= @para")

    # Check for INtensivzeit
    if parameters.get("ss_icu_checkbox", None):
        if parameters["ss_icu_von"]:
            para = int(parameters['ss_icu_von'])
            # df.query("ss_icu_von >= @para", inplace=True)
            sort_df("ss_icu_von >= @para")
        if parameters["ss_icu_bis"]:
            para = int(parameters['ss_icu_bis'])
            # df.query("ss_icu <= @para", inplace=True)
            sort_df("ss_icu <= @para")

    #  Check for LOS
    if parameters.get("ss_los_checkbox", None):
        if parameters["ss_los_von"]:
            para = int(parameters['ss_los_von'])
            # df.query("ss_los >= @para", inplace=True)
            sort_df("ss_los >= @para")
        if parameters["ss_los_bis"]:
            para = int(parameters['ss_los_bis'])
            # df.query("ss_los <= @para", inplace=True)
            sort_df("ss_los <= @para")

    # Check for DINDO
    if parameters.get('ss_dindo_checkbox', None):

        paralist = []
        if parameters.get('ss_check_dindo_0', None): paralist.append('No comp'); paralist.append('No comp'); print(
            "No Complications")
        if parameters.get('ss_check_dindo_1', None): paralist.append('I'); print("I")
        if parameters.get('ss_check_dindo_2', None): paralist.append('II'); print("II")
        if parameters.get('ss_check_dindo_3a', None): paralist.append('IIIa'); print("IIIa")
        if parameters.get('ss_check_dindo_3b', None): paralist.append('IIIb'); print("IIIb")
        if parameters.get('ss_check_dindo_4a', None): paralist.append('IVa'); print("IVa")
        if parameters.get('ss_check_dindo_4b', None): paralist.append('IVb'); print("IVb")
        if parameters.get('ss_check_dindo_5', None): paralist.append('V'); print("V")
        print(paralist)
        # df.query("ss_dindo in @paralist", inplace=True)
        sort_df("ss_dindo in @paralist")

    # Check for Laborparameters Second OP

    # #check for SerumBili ss

    # # Check for POD1
    if parameters.get("ss_serum_bili_pod1_checkbox", None):
        if parameters["ss_Serum_Bili_POD1_von"]:
            para = int(parameters['ss_Serum_Bili_POD1_von'])
            # df.query("ss_Serum_Bili_POD1 >= @para", inplace= True)
            sort_df("ss_Serum_Bili_POD1 >= @para")
        if parameters["ss_Serum_Bili_POD1_bis"]:
            para = int(parameters['ss_Serum_Bili_POD1_bis'])
            # df.query("ss_Serum_Bili_POD1 <= @para", inplace= True)
            sort_df("ss_Serum_Bili_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ss_serum_bili_pod3_checkbox", None):
        if parameters["ss_Serum_Bili_POD3_von"]:
            para = int(parameters['ss_Serum_Bili_POD3_von'])
            # df.query("ss_Serum_Bili_POD3 >= @para", inplace= True)
            sort_df("ss_Serum_Bili_POD3 >= @para")
        if parameters["ss_Serum_Bili_POD3_bis"]:
            para = int(parameters['ss_Serum_Bili_POD3_bis'])
            # df.query("ss_Serum_Bili_POD3 <= @para", inplace= True)
            sort_df("ss_Serum_Bili_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ss_serum_bili_pod5_checkbox", None):
        if parameters["ss_Serum_Bili_POD5_von"]:
            para = int(parameters['ss_Serum_Bili_POD5_von'])
            # df.query("ss_Serum_Bili_POD5 >= @para", inplace= True)
            sort_df("ss_Serum_Bili_POD5 >= @para")
        if parameters["ss_Serum_Bili_POD5_bis"]:
            para = int(parameters['ss_Serum_Bili_POD5_bis'])
            # df.query("ss_Serum_Bili_POD5 <= @para", inplace= True)
            sort_df("ss_Serum_Bili_POD5 <= @para")

    # # Check for Last
    if parameters.get("ss_serum_bili_last_checkbox", None):
        if parameters["ss_Serum_Bili_last_von"]:
            para = int(parameters['ss_Serum_Bili_last_von'])
            # df.query("ss_Serum_Bili_Last >= @para", inplace= True)
            sort_df("ss_Serum_Bili_Last >= @para")
        if parameters["ss_Serum_Bili_last_bis"]:
            para = int(parameters['ss_Serum_Bili_last_bis'])
            # df.query("ss_Serum_Bili_Last <= @para", inplace= True)
            sort_df("ss_Serum_Bili_Last <= @para")

    # #check for Drain Bili ss

    # # Check for POD1
    if parameters.get("ss_drain_bili_pod1_checkbox", None):
        if parameters["ss_drain_Bili_pod1_von"]:
            para = int(parameters['ss_drain_Bili_pod1_von'])
            # df.query("ss_Drain_Bili_POD1 >= @para", inplace= True)
            sort_df("ss_Drain_Bili_POD1 >= @para")
        if parameters["ss_drain_Bili_pod1_bis"]:
            para = int(parameters['ss_drain_Bili_pod1_bis'])
            # df.query("ss_Drain_Bili_POD1 <= @para", inplace= True)
            sort_df("ss_Drain_Bili_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ss_drain_bili_pod3_checkbox", None):
        if parameters["ss_drain_Bili_pod3_von"]:
            para = int(parameters['ss_drain_Bili_pod3_von'])
            # df.query("ss_Drain_Bili_POD3 >= @para", inplace= True)
            sort_df("ss_Drain_Bili_POD3 >= @para")
        if parameters["ss_drain_Bili_pod3_bis"]:
            para = int(parameters['ss_drain_Bili_pod3_bis'])
            # df.query("ss_Drain_Bili_POD3 <= @para", inplace= True)
            sort_df("ss_Drain_Bili_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ss_drain_bili_pod5_checkbox", None):
        if parameters["ss_drain_Bili_pod5_von"]:
            para = int(parameters['ss_drain_Bili_pod5_von'])
            # df.query("ss_Drain_Bili_POD5 >= @para", inplace= True)
            sort_df("ss_Drain_Bili_POD5 >= @para")
        if parameters["ss_drain_Bili_pod5_bis"]:
            para = int(parameters['ss_drain_Bili_pod5_bis'])
            # df.query("ss_Drain_Bili_POD5 <= @para", inplace= True)
            sort_df("ss_Drain_Bili_POD5 <= @para")

    # # Check for Last
    if parameters.get("ss_drain_bili_last_checkbox", None):
        if parameters["ss_drain_Bili_last_von"]:
            para = int(parameters['ss_drain_Bili_last_von'])
            # df.query("ss_Drain_Bili_Last >= @para", inplace= True)
            sort_df("ss_Drain_Bili_Last >= @para")
        if parameters["ss_drain_Bili_last_bis"]:
            para = int(parameters['ss_drain_Bili_last_bis'])
            # df.query("ss_Drain_Bili_Last <= @para", inplace= True)
            sort_df("ss_Drain_Bili_Last <= @para")

    # #Check for AST
    # # Check for POD1
    if parameters.get("ss_AST_pod1_checkbox", None):
        if parameters["ss_AST_pod1_von"]:
            para = int(parameters['ss_AST_pod1_von'])
            # df.query("ss_AST_POD1 >= @para", inplace= True)
            sort_df("ss_AST_POD1 >= @para")
        if parameters["ss_AST_pod1_bis"]:
            para = int(parameters['ss_AST_pod1_bis'])
            # df.query("ss_AST_POD1 <= @para", inplace= True)
            sort_dt("ss_AST_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ss_AST_pod3_checkbox", None):
        if parameters["ss_AST_pod3_von"]:
            para = int(parameters['ss_AST_pod3_von'])
            # df.query("ss_AST_POD3 >= @para", inplace= True)
            sort_df("ss_AST_POD3 >= @para")
        if parameters["ss_AST_pod3_bis"]:
            para = int(parameters['ss_AST_pod3_bis'])
            # df.query("ss_AST_POD3 <= @para", inplace= True)
            sort_df("ss_AST_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ss_AST_pod5_checkbox", None):
        if parameters["ss_AST_pod5_von"]:
            para = int(parameters['ss_AST_pod5_von'])
            # df.query("ss_AST_POD5 >= @para", inplace= True)
            sort_df("ss_AST_POD5 >= @para")
        if parameters["ss_AST_pod5_bis"]:
            para = int(parameters['ss_AST_pod5_bis'])
            # df.query("ss_AST_POD5 <= @para", inplace= True)
            sort_df("ss_AST_POD5 <= @para")

    # # Check for Last
    if parameters.get("ss_AST_last_checkbox", None):
        if parameters["ss_AST_last_von"]:
            para = int(parameters['ss_AST_last_von'])
            # df.query("ss_AST_Last >= @para", inplace= True)
            sort_df("ss_AST_Last >= @para")
        if parameters["ss_AST_last_bis"]:
            para = int(parameters['ss_AST_last_bis'])
            # df.query("ss_AST_Last <= @para", inplace= True)
            sort_df("ss_AST_Last <= @para")

    # #Check for ALT ss
    # # Check for POD1
    if parameters.get("ss_ALT_pod1_checkbox", None):
        if parameters["ss_ALT_pod1_von"]:
            para = int(parameters['ss_ALT_pod1_von'])
            # df.query("ss_ALT_POD1 >= @para", inplace= True)
            sort_df("ss_ALT_POD1 >= @para")
        if parameters["ss_ALT_pod1_bis"]:
            para = int(parameters['ss_ALT_pod1_bis'])
            # df.query("ss_ALT_POD1 <= @para", inplace= True)
            sort_df("ss_ALT_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ss_ALT_pod3_checkbox", None):
        if parameters["ss_ALT_pod3_von"]:
            para = int(parameters['ss_ALT_pod3_von'])
            # df.query("ss_ALT_POD3 >= @para", inplace= True)
            sort_df("ss_ALT_POD3 >= @para")
        if parameters["ss_ALT_pod3_bis"]:
            para = int(parameters['ss_ALT_pod3_bis'])
            # df.query("ss_ALT_POD3 <= @para", inplace= True)
            sort_df("ss_ALT_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ss_ALT_pod5_checkbox", None):
        if parameters["ss_ALT_pod5_von"]:
            para = int(parameters['ss_ALT_pod5_von'])
            # df.query("ss_ALT_POD5 >= @para", inplace= True)
            sort_df("ss_ALT_POD5 >= @para")
        if parameters["ss_ALT_pod5_bis"]:
            para = int(parameters['ss_ALT_pod5_bis'])
            # df.query("ss_ALT_POD5 <= @para", inplace= True)
            sort_df("ss_ALT_POD5 <= @para")

    # # Check for Last
    if parameters.get("ss_ALT_Last_checkbox", None):
        if parameters["ss_ALT_Last_von"]:
            para = int(parameters['ss_ALT_Last_von'])
            # df.query("ss_ALT_Last >= @para", inplace= True)
            sort_df("ss_ALT_Last >= @para")
        if parameters["ss_ALT_Last_bis"]:
            para = int(parameters['ss_ALT_Last_bis'])
            # df.query("ss_ALT_Last <= @para", inplace= True)
            sort_df("ss_ALT_Last <= @para")

    # #Check for INR
    if parameters.get("ss_INR_pod1_checkbox", None):
        if parameters["ss_INR_pod1_von"]:
            para = int(parameters['ss_INR_pod1_von'])
            # df.query("ss_INR_POD1 >= @para", inplace= True)
            sort_df("ss_INR_POD1 >= @para")
        if parameters["ss_INR_pod1_bis"]:
            para = int(parameters['ss_INR_pod1_bis'])
            # df.query("ss_INR_POD1 <= @para", inplace= True)
            sort_df("ss_INR_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ss_INR_pod3_checkbox", None):
        if parameters["ss_INR_pod3_von"]:
            para = int(parameters['ss_INR_pod3_von'])
            # df.query("ss_INR_POD3 >= @para", inplace= True)
            sort_df("ss_INR_POD3 >= @para")
        if parameters["ss_INR_pod3_bis"]:
            para = int(parameters['ss_INR_pod3_bis'])
            # df.query("ss_INR_POD3 <= @para", inplace= True)
            sort_df("ss_INR_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ss_INR_pod5_checkbox", None):
        if parameters["ss_INR_pod5_von"]:
            para = int(parameters['ss_INR_pod5_von'])
            # df.query("ss_INR_POD5 >= @para", inplace= True)
            sort_df("ss_INR_POD5 >= @para")
        if parameters["ss_INR_pod5_bis"]:
            para = int(parameters['ss_INR_pod5_bis'])
            # df.query("ss_INR_POD5 <= @para", inplace= True)
            sort_df("ss_INR_POD5 <= @para")

    # # Check for Last
    if parameters.get("ss_INR_Last_checkbox", None):
        if parameters["ss_INR_Last_von"]:
            para = int(parameters['ss_INR_Last_von'])
            # df.query("ss_INR_Last >= @para", inplace= True)
            sort_df("ss_INR_Last >= @para")
        if parameters["ss_INR_Last_bis"]:
            para = int(parameters['ss_INR_Last_bis'])
            # df.query("ss_INR_Last <= @para", inplace= True)
            sort_df("ss_INR_Last <= @para")

    # Third Op Data
    if parameters.get("ts_op_date", None):
        if parameters.get('op_date_Surgery3_von', None):
            von_date = datetime.datetime.strptime(parameters['op_date_Surgery3_von'], constants.DATEFORMAT)
            von_date = datetime.date(von_date.year, von_date.month, von_date.day)
            print(von_geburt)
            # df.query("op_date_Surgery3 >= @von_date",inplace=True)
            sort_df("op_date_Surgery3 >= @von_date")
        if parameters.get('op_date_Surgery3', None):
            bis_date = datetime.datetime.strptime(parameters['limax_third_date_bis'], constants.DATEFORMAT)
            bis_date = datetime.date(bis_date.year, bis_date.month, bis_date.day)
            print(von_geburt)
            # df.query("op_date_Surgery3 <= @bis_date",inplace=True)
            sort_df("op_date_Surgery3 <= @bis_date")

    # Check for Second Op Code
    if parameters.get("op_code_Surgery3_checkbox", None):
        if parameters['op_code_Surgery3']:
            print(type(parameters['op_code_Surgery3']))
            # df.query("op_code_Surgery3 == @parameters['op_code_Surgery3']",inplace=True)
            sort_df("op_code_Surgery3 == @parameters['op_code_Surgery3']")

    # Check for Second OP Diagnosis
    if parameters.get("op_diagnosis_Surgery3_checkbox", None):
        if parameters['op_diagnosis_Surgery3']:
            print(type(parameters['op_diagnosis_Surgery3']))
            # df.query("op_diagnosis_Surgery3 == @parameters['op_diagnosis_Surgery3']",inplace=True)
            sort_df("op_diagnosis_Surgery3 == @parameters['op_diagnosis_Surgery3']")

    print(parameters)

    # Check for OP Methode
    if parameters.get('ts_op_method_checkbox', None):

        paralist = []
        if parameters.get('ts_checkoffen', None): paralist.append('offen'); print("offen")
        if parameters.get('ts_checklaparoskopisch', None): paralist.append('laparoskopisch');print("laparoskopisch")
        if parameters.get('ts_checkrobo', None): paralist.append('robotisch');print("checkrobo")
        # df.query("third_surgery_minimal_invasive in @paralist", inplace=True)
        sort_df("third_surgery_minimal_invasive in @paralist")

    # Check for OP Konversion
    if parameters.get('ts_op_occurence_checkbox', None):
        if parameters['op3_conversion_check']:
            # df.query("third_surgery_conversion == 1",inplace=True)
            sort_df("third_surgery_conversion == 1")
        if parameters['op3_ablation_check']:
            # df.query("third_surgery_ablation == 1",inplace=True)
            sort_df("third_surgery_ablation == 1")

    # Check for Length
    if parameters.get("ts_op_length_checkbox", None):
        if parameters["op_length_von"]:
            para = int(parameters['op_length_von'])
            # df.query("third_surgery_length >= @para", inplace=True)
            sort_df("third_surgery_length >= @para")
        if parameters["ts_op_length_bis"]:
            para = int(parameters['op_length_bis'])
            # df.query("third_surgery_length <= @para", inplace=True)
            sort_df("third_surgery_length <= @para")

    # Check for INtensivzeit
    if parameters.get("ts_icu_checkbox", None):
        if parameters["ts_icu_von"]:
            para = int(parameters['ts_icu_von'])
            # df.query("ts_icu_von >= @para", inplace=True)
            sort_df("ts_icu_von >= @para")
        if parameters["ts_icu_bis"]:
            para = int(parameters['ts_icu_bis'])
            # df.query("ts_icu <= @para", inplace=True)
            sort_df("ts_icu <= @para")

    #  Check for LOS
    if parameters.get("ts_los_checkbox", None):
        if parameters["ts_los_von"]:
            para = int(parameters['ts_los_von'])
            # df.query("ts_los >= @para", inplace=True)
            sort_df("ts_los >= @para")
        if parameters["ts_los_bis"]:
            para = int(parameters['ts_los_bis'])
            # df.query("ts_los <= @para", inplace=True)
            sort_df("ts_los <= @para")

    # Check for DINDO
    if parameters.get('ts_dindo_checkbox', None):

        paralist = []
        if parameters.get('ts_check_dindo_0', None): paralist.append('No comp'); paralist.append('No comp'); print(
            "No Complications")
        if parameters.get('ts_check_dindo_1', None): paralist.append('I'); print("I")
        if parameters.get('ts_check_dindo_2', None): paralist.append('II'); print("II")
        if parameters.get('ts_check_dindo_3a', None): paralist.append('IIIa'); print("IIIa")
        if parameters.get('ts_check_dindo_3b', None): paralist.append('IIIb'); print("IIIb")
        if parameters.get('ts_check_dindo_4a', None): paralist.append('IVa'); print("IVa")
        if parameters.get('ts_check_dindo_4b', None): paralist.append('IVb'); print("IVb")
        if parameters.get('ts_check_dindo_5', None): paralist.append('V'); print("V")
        print(paralist)
        # df.query("ts_dindo in @paralist", inplace=True)
        sort_df("ts_dindo in @paralist")

    # Check for Third OP Labor
    # Check for Laborparameters Second OP

    # #check for SerumBili ss

    # # Check for POD1
    if parameters.get("ts_serum_bili_pod1_checkbox", None):
        if parameters["ts_Serum_Bili_POD1_von"]:
            para = int(parameters['ts_Serum_Bili_POD1_von'])
            # df.query("ts_Serum_Bili_POD1 >= @para", inplace= True)
            sort_df("ts_Serum_Bili_POD1 >= @para")
        if parameters["ts_Serum_Bili_POD1_bis"]:
            para = int(parameters['ts_Serum_Bili_POD1_bis'])
            # df.query("ts_Serum_Bili_POD1 <= @para", inplace= True)
            sort_df("ts_Serum_Bili_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ts_serum_bili_pod3_checkbox", None):
        if parameters["ts_Serum_Bili_POD3_von"]:
            para = int(parameters['ts_Serum_Bili_POD3_von'])
            # df.query("ts_Serum_Bili_POD3 >= @para", inplace= True)
            sort_df("ts_Serum_Bili_POD3 >= @para")
        if parameters["ts_Serum_Bili_POD3_bis"]:
            para = int(parameters['ts_Serum_Bili_POD3_bis'])
            # df.query("ts_Serum_Bili_POD3 <= @para", inplace= True)
            sort_df("ts_Serum_Bili_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ts_serum_bili_pod5_checkbox", None):
        if parameters["ts_Serum_Bili_POD5_von"]:
            para = int(parameters['ts_Serum_Bili_POD5_von'])
            # df.query("ts_Serum_Bili_POD5 >= @para", inplace= True)
            sort_df("ts_Serum_Bili_POD5 >= @para")
        if parameters["ts_Serum_Bili_POD5_bis"]:
            para = int(parameters['ts_Serum_Bili_POD5_bis'])
            # df.query("ts_Serum_Bili_POD5 <= @para", inplace= True)
            sort_df("ts_Serum_Bili_POD5 <= @para")

    # # Check for Last
    if parameters.get("ts_serum_bili_last_checkbox", None):
        if parameters["ts_Serum_Bili_last_von"]:
            para = int(parameters['ts_Serum_Bili_last_von'])
            # df.query("ts_Serum_Bili_Last >= @para", inplace= True)
            sort_df("ts_Serum_Bili_Last >= @para")
        if parameters["ts_Serum_Bili_last_bis"]:
            para = int(parameters['ts_Serum_Bili_last_bis'])
            # df.query("ts_Serum_Bili_Last <= @para", inplace= True)
            sort_df("ts_Serum_Bili_Last <= @para")

    # #check for Drain Bili ss

    # # Check for POD1
    if parameters.get("ts_drain_bili_pod1_checkbox", None):
        if parameters["ts_drain_Bili_pod1_von"]:
            para = int(parameters['ts_drain_Bili_pod1_von'])
            # df.query("ts_Drain_Bili_POD1 >= @para", inplace= True)
            sort_df("ts_Drain_Bili_POD1 >= @para")
        if parameters["ts_drain_Bili_pod1_bis"]:
            para = int(parameters['ts_drain_Bili_pod1_bis'])
            # df.query("ts_Drain_Bili_POD1 <= @para", inplace= True)
            sort_df("ts_Drain_Bili_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ts_drain_bili_pod3_checkbox", None):
        if parameters["ts_drain_Bili_pod3_von"]:
            para = int(parameters['ts_drain_Bili_pod3_von'])
            # df.query("ts_Drain_Bili_POD3 >= @para", inplace= True)
            sort_df("ts_Drain_Bili_POD3 >= @para")
        if parameters["ts_drain_Bili_pod3_bis"]:
            para = int(parameters['ts_drain_Bili_pod3_bis'])
            # df.query("ts_Drain_Bili_POD3 <= @para", inplace= True)
            sort_df("ts_Drain_Bili_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ts_drain_bili_pod5_checkbox", None):
        if parameters["ts_drain_Bili_pod5_von"]:
            para = int(parameters['ts_drain_Bili_pod5_von'])
            # df.query("ts_Drain_Bili_POD5 >= @para", inplace= True)
            sort_df("ts_Drain_Bili_POD5 >= @para")
        if parameters["ts_drain_Bili_pod5_bis"]:
            para = int(parameters['ts_drain_Bili_pod5_bis'])
            # df.query("ts_Drain_Bili_POD5 <= @para", inplace= True)
            sort_df("ts_Drain_Bili_POD5 <= @para")

    # # Check for Last
    if parameters.get("ts_drain_bili_last_checkbox", None):
        if parameters["ts_drain_Bili_last_von"]:
            para = int(parameters['ts_drain_Bili_last_von'])
            # df.query("ts_Drain_Bili_Last >= @para", inplace= True)
            sort_df("ts_Drain_Bili_Last >= @para")
        if parameters["ts_drain_Bili_last_bis"]:
            para = int(parameters['ts_drain_Bili_last_bis'])
            # df.query("ts_Drain_Bili_Last <= @para", inplace= True)
            sort_df("ts_Drain_Bili_Last <= @para")

    # #Check for AST
    # # Check for POD1
    if parameters.get("ts_AST_pod1_checkbox", None):
        if parameters["ts_AST_pod1_von"]:
            para = int(parameters['ts_AST_pod1_von'])
            # df.query("ts_AST_POD1 >= @para", inplace= True)
            sort_df("ts_AST_POD1 >= @para")
        if parameters["ts_AST_pod1_bis"]:
            para = int(parameters['ts_AST_pod1_bis'])
            # df.query("ts_AST_POD1 <= @para", inplace= True)
            sort_df("ts_AST_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ts_AST_pod3_checkbox", None):
        if parameters["ts_AST_pod3_von"]:
            para = int(parameters['ts_AST_pod3_von'])
            # df.query("ts_AST_POD3 >= @para", inplace= True)
            sort_df("ts_AST_POD3 >= @para")
        if parameters["ts_AST_pod3_bis"]:
            para = int(parameters['ts_AST_pod3_bis'])
            # df.query("ts_AST_POD3 <= @para", inplace= True)
            sort_df("ts_AST_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ts_AST_pod5_checkbox", None):
        if parameters["ts_AST_pod5_von"]:
            para = int(parameters['ts_AST_pod5_von'])
            # df.query("ts_AST_POD5 >= @para", inplace= True)
            sort_df("ts_AST_POD5 >= @para")
        if parameters["ts_AST_pod5_bis"]:
            para = int(parameters['ts_AST_pod5_bis'])
            # df.query("ts_AST_POD5 <= @para", inplace= True)
            sort_df("ts_AST_POD5 <= @para")

    # # Check for Last
    if parameters.get("ts_AST_last_checkbox", None):
        if parameters["ts_AST_last_von"]:
            para = int(parameters['ts_AST_last_von'])
            # f.query("ts_AST_Last >= @para", inplace= True)
            sort_df("ts_AST_Last >= @para")
        if parameters["ts_AST_last_bis"]:
            para = int(parameters['ts_AST_last_bis'])
            # df.query("ts_AST_Last <= @para", inplace= True)
            sort_df("ts_AST_Last <= @para")

    # #Check for ALT ss
    # # Check for POD1
    if parameters.get("ts_ALT_pod1_checkbox", None):
        if parameters["ts_ALT_pod1_von"]:
            para = int(parameters['ts_ALT_pod1_von'])
            # df.query("ts_ALT_POD1 >= @para", inplace= True)
            sort_df("ts_ALT_POD1 >= @para")
        if parameters["ts_ALT_pod1_bis"]:
            para = int(parameters['ts_ALT_pod1_bis'])
            # df.query("ts_ALT_POD1 <= @para", inplace= True)
            sort_df("ts_ALT_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ts_ALT_pod3_checkbox", None):
        if parameters["ts_ALT_pod3_von"]:
            para = int(parameters['ts_ALT_pod3_von'])
            # df.query("ts_ALT_POD3 >= @para", inplace= True)
            sort_df("ts_ALT_POD3 >= @para")
        if parameters["ts_ALT_pod3_bis"]:
            para = int(parameters['ts_ALT_pod3_bis'])
            # df.query("ts_ALT_POD3 <= @para", inplace= True)
            sort_df("ts_ALT_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ts_ALT_pod5_checkbox", None):
        if parameters["ts_ALT_pod5_von"]:
            para = int(parameters['ts_ALT_pod5_von'])
            # df.query("ts_ALT_POD5 >= @para", inplace= True)
            sort_df("ts_ALT_POD5 >= @para")
        if parameters["ts_ALT_pod5_bis"]:
            para = int(parameters['ts_ALT_pod5_bis'])
            # df.query("ts_ALT_POD5 <= @para", inplace= True)
            sort_df("ts_ALT_POD5 <= @para")

    # # Check for Last
    if parameters.get("ts_ALT_Last_checkbox", None):
        if parameters["ts_ALT_Last_von"]:
            para = int(parameters['ts_ALT_Last_von'])
            # df.query("ts_ALT_Last >= @para", inplace= True)
            sort_df("ts_ALT_Last >= @para")
        if parameters["ts_ALT_Last_bis"]:
            para = int(parameters['ts_ALT_Last_bis'])
            # df.query("ts_ALT_Last <= @para", inplace= True)
            sort_df("ts_ALT_Last <= @para")

    # #Check for INR
    if parameters.get("ts_INR_pod1_checkbox", None):
        if parameters["ts_INR_pod1_von"]:
            para = int(parameters['ts_INR_pod1_von'])
            # df.query("ts_INR_POD1 >= @para", inplace= True)
            sort_df("ts_INR_POD1 >= @para")
        if parameters["ts_INR_pod1_bis"]:
            para = int(parameters['ts_INR_pod1_bis'])
            # df.query("ts_INR_POD1 <= @para", inplace= True)
            sort_df("ts_INR_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ts_INR_pod3_checkbox", None):
        if parameters["ts_INR_pod3_von"]:
            para = int(parameters['ts_INR_pod3_von'])
            # df.query("ts_INR_POD3 >= @para", inplace= True)
            sort_df("ts_INR_POD3 >= @para")
        if parameters["ts_INR_pod3_bis"]:
            para = int(parameters['ts_INR_pod3_bis'])
            # df.query("ts_INR_POD3 <= @para", inplace= True)
            sort_df("ts_INR_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ts_INR_pod5_checkbox", None):
        if parameters["ts_INR_pod5_von"]:
            para = int(parameters['ts_INR_pod5_von'])
            # df.query("ts_INR_POD5 >= @para", inplace= True)
            sort_df("ts_INR_POD5 >= @para")
        if parameters["ts_INR_pod5_bis"]:
            para = int(parameters['ts_INR_pod5_bis'])
            # df.query("ts_INR_POD5 <= @para", inplace= True)
            sort_df("ts_INR_POD5 <= @para")

    # # Check for Last
    if parameters.get("ts_INR_Last_checkbox", None):
        if parameters["ts_INR_Last_von"]:
            para = int(parameters['ts_INR_Last_von'])
            # df.query("ts_INR_Last >= @para", inplace= True)
            sort_df("ts_INR_Last >= @para")
        if parameters["ts_INR_Last_bis"]:
            para = int(parameters['ts_INR_Last_bis'])
            # df.query("ts_INR_Last <= @para", inplace= True)
            sort_df("ts_INR_Last <= @para")

    df.fillna("None")

    if Mode:
        return df_AND
    else:
        return df_or
