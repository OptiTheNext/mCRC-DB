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


def data_output(parameters) -> pandas.DataFrame:
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

    # Entferne Spalten ohne Kürzel -> Entferne noch nicht bearbeitete Zeilen
    df.query("Kuerzel != ''", inplace=True)

    # Convert Booleans into Python Booleans

    df = df.apply(pandas.to_numeric, errors="ignore")
    df['pve'] = df['pve'].fillna(False).astype('bool')
    df['dob'] = pandas.to_datetime(df.dob)
    df['crlm_bilobular'] = df['crlm_bilobular'].fillna(False).astype('bool')
    df['multimodal'] = df['multimodal'].fillna(False).astype('bool')
    df['two_staged'] = df['two_staged'].fillna(False).astype('bool')
    df['status_fu'] = df['status_fu'].fillna(False).astype('bool')
    df['recurrence_status'] = df['recurrence_status'].fillna(False).astype('bool')
    df['Pn'] = df['Pn'].fillna(False).astype('string')
    df['alcohol'] = df['alcohol'].fillna(False).astype('bool')
    df['smoking'] = df['smoking'].fillna(False).astype('bool')
    df['diabetes'] = df['diabetes'].fillna(False).astype('bool')
    df['cirrhosis'] = df['cirrhosis'].fillna(False).astype('bool')
    df['fibrosis'] = df['fibrosis'].fillna(False).astype('bool')
    df['fs_previous_chemotherapy'] = df['fs_previous_chemotherapy'].fillna(False).astype('bool')
    df["ss_previous_chemotherapy"]=df["ss_previous_chemotherapy"].replace({0: False, 1: True})
    df["th_previous_chemotherapy"]=df["th_previous_chemotherapy"].replace({0: False, 1: True})
    df['first_surgery_ablation'] = df['first_surgery_ablation'].fillna(False).astype('bool')
    df['first_surgery_conversion'] = df['first_surgery_conversion'].fillna(False).astype('bool')
    df["second_surgery_planned"]=df["second_surgery_planned"].replace({"0": False, "1": True})
    df["second_surgery_realized"]=df["second_surgery_realized"].replace({0: False, 1: True})
    df["second_surgery_conversion"]=df["second_surgery_conversion"].replace({0: False, 1: True})
    df["second_surgery_ablation"]=df["third_surgery_ablation"].replace({0: False, 1: True})
    df["third_surgery_conversion"]=df["third_surgery_conversion"].replace({0: False, 1: True})
    df["third_surgery_ablation"]=df["second_surgery_ablation"].replace({0: False, 1: True})
    df["third_surgery_planned"]=df["third_surgery_planned"].replace({0: False, 1: True})
    df["third_surgery_realized"]=df["third_surgery_realized"].replace({0: False, 1: True})
    df["third_surgery_conversion"]=df["third_surgery_conversion"].replace({"0": False, "1": True})
    df["third_surgery_ablation"]=df["third_surgery_ablation"].replace({"0": False, "1": True})
    df['op_date_Surgery1'] = pandas.to_datetime(df["op_date_Surgery1"],format=constants.DATEFORMAT,errors='coerce')
    df['op_date_Surgery2'] = pandas.to_datetime(df["op_date_Surgery2"],format =constants.DATEFORMAT,errors='coerce')
    df['op_date_Surgery3'] = pandas.to_datetime(df["op_date_Surgery3"],format =constants.DATEFORMAT,errors='coerce')
    df['limax_initial_date'] = pandas.to_datetime(df["limax_initial_date"],format =constants.DATEFORMAT,errors='coerce')
    df['limax_second_date'] = pandas.to_datetime(df["limax_second_date"],format =constants.DATEFORMAT,errors='coerce')
    df['limax_third_date'] = pandas.to_datetime(df["limax_third_date"],format =constants.DATEFORMAT,errors='coerce')
    df['diagnosis_date'] = pandas.to_datetime(df["diagnosis_date"],format=constants.DATEFORMAT,errors='coerce')
    df['previous_surgery_date'] = pandas.to_datetime(df["previous_surgery_date"],format=constants.DATEFORMAT,errors='coerce')

  
    if parameters.get("Mode"):
        global Mode
        if parameters['Mode'] == "additiv":
            Mode = True
        if parameters['Mode'] == "subtraktiv":
            Mode = False

    global df_AND
    df_AND = df

    def sort_df(string):
        if Mode:
            global df_AND
            df_AND = df_AND.query(string)
        if not Mode:
            global df_or
            temp_df = df.query(string)
            df_or = pandas.concat([df_or, temp_df]).drop_duplicates() 
    # Beginn des Filterns

    # Check für SAPID

    if parameters.get('pat_id_check', None) and parameters["pat_id"]:
        global pat_id
        pat_id = int(parameters['pat_id'])
        sort_df("pat_id == @pat_id")

    # Check for Geburtsdatum
    if parameters.get('geburtcheck', None):
        if parameters['von_geburt']:
            global von_geburt
            von_geburt = datetime.datetime.strptime(parameters['von_geburt'], constants.DATEFORMAT)
            von_geburt = datetime.date(von_geburt.year, von_geburt.month, von_geburt.day)
            sort_df("dob >= @von_geburt")
        if parameters["bis_geburt"]:
            global bis_geburt
            bis_geburt = datetime.datetime.strptime(parameters['bis_geburt'], constants.DATEFORMAT)
            bis_geburt = datetime.date(bis_geburt.year, bis_geburt.month, bis_geburt.day)
            sort_df("dob <= @bis_geburt")

    # Check for Sex
    if parameters.get('sexcheck', None):
        global sexlist
        sexlist = []
        if parameters.get('männlichcheck', None):
            sexlist.append('m')
        if parameters.get('weiblichcheck', None):
            sexlist.append('f')
        sort_df("sex in @sexlist")

    # Check for Diagnose Codes
    if parameters.get("diagnose_code_check", None):
        if parameters['diagnosis1']:
            para = parameters['diagnosis1']
            sort_df("diagnosis1 == @para")
        if parameters["diagnosis2"]:
            para = parameters['diagnosis2']
            sort_df("diagnosis2 == @para")

    # Check for Diagnosis Date
    if parameters.get("diagnosis_date_check", None):
        if parameters['von_diagnosis_date']:
            global von_diagnosis_date
            von_diagnosis_date = datetime.datetime.strptime(parameters['von_diagnosis_date'], constants.DATEFORMAT)
            von_diagnosis_date = datetime.date(von_diagnosis_date.year, von_diagnosis_date.month,
                                               von_diagnosis_date.day)
            sort_df("diagnosis_date >= @von_diagnosis_date")
        if parameters["bis_diagnosis_date"]:
            global bis_diagnosis_date
            bis_diagnosis_date = datetime.datetime.strptime(parameters['bis_diagnosis_date'], constants.DATEFORMAT)
            bis_diagnosis_date = datetime.date(bis_diagnosis_date.year, bis_diagnosis_date.month,
                                               bis_diagnosis_date.day)
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
        sort_df("primary_location in @locations")

    # Check for Synchron/Metachron
    if parameters.get('crlm_met_syn_check', None):
        global crlm_list
        crlm_list = []
        if parameters.get('Synchron_check', None): crlm_list.append('synchron')
        if parameters.get('Metachron_check', None): crlm_list.append('metachron')
        sort_df("crlm_met_syn in @crlm_list")

    # check for Bilobulär#
    if parameters.get('bilobulär_check', None):
        if parameters.get('bilobulär_check_yes', None):
            sort_df("crlm_bilobular == 1")
        if parameters.get('bilobulär_check_no', None):
            sort_df("crlm_bilobular == 0")

    # Check for Multimodal

    if parameters.get('multimodal_check', None):
        if parameters.get('multimodal_check_yes', None):
            sort_df("multimodal == 1")
        if parameters.get('multimodal_check_no', None):
            sort_df("multimodal == 0")

    # Check for twostaged
    if parameters.get('twostaged_check', None):
        if parameters.get('twostaged_check_yes', None):
            sort_df("two_staged==1")
        if parameters.get('twostaged_check_no', None):
            sort_df("two_staged==0")

    # Check for BRAF
    if parameters.get('braf_check', None):
        global braf
        braf = []
        if parameters.get('braf_mutiert_check', None): braf.append('mut')
        if parameters.get('braf_wildtyp_check', None): braf.append('wt')
        sort_df("BRAF in @braf")

    # Check for RAS
    if parameters.get('ras_check', None):
        global ras
        ras = []
        if parameters.get('ras_mutiert_check', None): ras.append('mut')
        if parameters.get('ras_wildtyp_check', None): ras.append('wt')
        sort_df("RAS in @ras")

    # Check for MSS
    if parameters.get('mss_check', None):
        global mss
        mss = []
        if parameters.get('mss', None): mss.append('mss')
        if parameters.get('msi', None): mss.append('msi')
        sort_df("MSS in @mss")
    # Check for T
    if parameters.get('t_check', None) and parameters["T"]:
        para = parameters['T']
        sort_df("T == @para")

    # Check for N
    if parameters.get('n_check', None) and parameters["N"]:
        para = parameters['N']
        sort_df("N == @para")

    # Check for M
    if parameters.get('m_check', None) and parameters["M"]:
        para = parameters['M']
        sort_df("M==@para")

    # Check for LK
    if parameters.get('lk_check', None) and parameters["LK"]:
        para = parameters['LK']
        sort_df("LK == @para")
    
        # Check for L
    if parameters.get('l_check', None) and parameters["L"]:
        para = int(parameters['L'])
        sort_df("L == @para")

    # Check for V
    if parameters.get('v_check', None) and parameters["V"]:
        para = int(parameters['V'])
        sort_df("V == @para")
    # Check for R
    if parameters.get('r_check', None) and parameters["R"]:
        para = int(parameters['R'])
        sort_df("R == @para")

    # Check for G
    if parameters.get('g_check', None) and parameters["G"]:
        para = int(parameters['G'])
        sort_df("G==@para")
    
    #Check for Pn
    if parameters.get('Pn_check', None) and parameters["Pn"]:
        para = parameters['Pn']
        sort_df("Pn==@para")

    # Check for Last Seen Date
    if parameters.get("last_seen_check", None):
        if parameters['date_fu_von']:
            global date_fu_von
            date_fu_von = datetime.datetime.strptime(parameters['date_fu_von'], constants.DATEFORMAT)
            date_fu_von = datetime.date(date_fu_von.year, date_fu_von.month, date_fu_von.day)
            sort_df("date_fu >= @date_fu_von")
        if parameters["date_fu_bis"]:
            global date_fu_bis
            date_fu_bis = datetime.datetime.strptime(parameters['date_fu_bis'], constants.DATEFORMAT)
            date_fu_bis = datetime.date(date_fu_bis.year, date_fu_bis.month, date_fu_bis.day)
            sort_df("date_fu <= @date_fu_bis")

    # Check for Alive or Not
    if parameters.get("died_check", None):
        if parameters.get("died_no_check", None):
            sort_df("status_fu == 1")
        if parameters.get("died_yes_check", None):
            sort_df("status_fu == 0")

    # Check for Rezidiv
    if parameters.get("rezidiv_check", None):
        if parameters.get("rezidiv_check_no", None):
            sort_df("recurrence_status == 0")
        if parameters.get("rezidiv_check_yes", None):
            sort_df("recurrence_status == 1")
    #Check for Rezidiv organ
    if parameters.get("rezidiv_organ",None):
        global organs
        organs = []
        if parameters.get('rezidiv_organ_leber', None): organs.append('liver')
        if parameters.get('rezidiv_organ_lunge', None): organs.append('lung')
        if parameters.get('rezidiv_organ_lokal', None): organs.append('lokal')
        if parameters.get('rezidiv_organ_peritoneum', None): organs.append('peritoneum')
        if parameters.get('rezidiv_organ_cerebral', None): organs.append('cerebral')
        if parameters.get('rezidiv_organ_other', None): organs.append('other')
        sort_df("recurrence_organ in @organs")

    # Check for ASA
    if parameters.get("asa_check", None):
        if parameters.get("asa_check_not_found", None):
            sort_df("asa== 0")
        if parameters.get("asa_check_1", None):
            sort_df("asa== 1")
        if parameters.get("asa_check_2", None):
            sort_df("asa== 2")
        if parameters.get("asa_check_3", None):
            sort_df("asa== 3")
        if parameters.get("asa_check_4", None):
            sort_df("asa== 4")
        if parameters.get("asa_check_5", None):
            sort_df("asa== 5")

    # Check for BMI
    if parameters.get("bmi_check", None):
        if parameters["von_bmi_input"]:
            para = parameters['von_bmi_input']
            sort_df("bmi >= @para")
        if parameters["bis_bmi_input"]:
            para = parameters['bis_bmi_input']
            sort_df("bmi <= @para")

    # Check for alc
    if parameters.get("alc_check", None):
        if parameters.get("yes_alcohol_check", None):
            sort_df("alcohol == 0")
        if parameters.get("no_alcohol_check", None):
            sort_df("alcohol == 1")

    # Check for Raucher
    if parameters.get("smoking_check", None):
        if parameters.get("smoking_check_yes", None):
            sort_df("smoking == 1")
        if parameters.get("smoking_check_no", None):
            sort_df("smoking == 0")

    # Check for Diabetiker
    if parameters.get("diabetes_check", None):
        if parameters.get("diabetes_check_yes", None):
            sort_df("diabetes  == 1")
        if parameters.get("diabetes_check_no", None):
            sort_df("diabetes  == 0")

    # Check for Zirrose
    if parameters.get("zirrose_check", None):
        if parameters.get("zirrose_check_yes", None):
            sort_df("cirrhosis   == 1")

        if parameters.get("zirrose_check_no", None):
            sort_df("cirrhosis   == 0")

    # Check for Fibrose
    if parameters.get("fibrose_check", None):
        if parameters.get("fibrose_check_yes", None):
            sort_df("fibrosis == 1")
        if parameters.get("fibrose_check_no", None):
            sort_df("fibrosis == 0")

    # Check for Previous OPs
    if parameters.get("PreviousOPs", None):
        if parameters["previous_surgery_code"]:
            para = parameters['previous_surgery_code']
            sort_df("previous_surgery == @para")
        if parameters['previous_surgery_date_von']:
            von_date = datetime.datetime.strptime(parameters['previous_surgery_date_von'], constants.DATEFORMAT)
            von_date = datetime.date(von_date.year, von_date.month, von_date.day)
            sort_df("previous_surgery_date >= @von_date")
        if parameters['previous_surgery_date_bis']:
            bis_date = datetime.datetime.strptime(parameters['previous_surgery_date_bis'], constants.DATEFORMAT)
            bis_date = datetime.date(bis_date.year, bis_date.month, bis_date.day)
            sort_df("previous_surgery_date <= @bis_date")

    # Check for FS_Chemo
    if parameters.get("fs_previous_chemotherapy", None):
        if parameters.get("fs_chemo_check_no", None):
            sort_df("op_date_Surgery1 != ''")
            sort_df("fs_previous_chemotherapy == 0")
        if parameters["fs_previous_chemotherapy_cycles_von"]:
            para = int(parameters['fs_previous_chemotherapy_cycles_von'])
            sort_df("fs_previous_chemotherapy_cycles >= @para")
        if parameters["fs_previous_chemotherapy_cycles_bis"]:
            para = int(parameters['fs_previous_chemotherapy_cycles_bis'])
            sort_df("fs_previous_chemotherapy_cycles <= @para")
        if parameters["fs_previous_chemotherapy_type"]:
            para = parameters['fs_previous_chemotherapy_type']
            sort_df("fs_previous_chemotherapy_type == @para")
        if parameters["fs_previous_antibody"]:
            para= parameters['fs_previous_antibody']
            sort_df("fs_previous_antibody == @para")

    # Check for SS_Chemo
    if parameters.get("ss_previous_chemotherapy", None):
        if parameters.get("ss_chemo_check_no", None):
            sort_df("op_date_Surgery2 != ''")
            sort_df("ss_previous_chemotherapy == 0")
        if parameters["ss_previous_chemotherapy_cycles_von"]:
            para = int(parameters['ss_previous_chemotherapy_cycles_von'])
            sort_df("ss_previous_chemotherapy_cycles >= @para")
        if parameters["ss_previous_chemotherapy_cycles_bis"]:
            para = int(parameters['ss_previous_chemotherapy_cycles_bis'])
            sort_df("ss_previous_chemotherapy_cycles <= @para")
        if parameters["ss_previous_chemotherapy_type"]:
            para = parameters['ss_previous_chemotherapy_type']
            sort_df("ss_previous_chemotherapy_type == @para")
        if parameters["ss_previous_antibody"]:
            para= parameters['ss_previous_antibody']
            # df.query("fs_previous_antibody = @parameters['fs_previous_antibody']",inplace=True)
            sort_df("ss_previous_antibody == @para")

    # Check for TH_Chemo
    if parameters.get("th_previous_chemotherapy", None):
        if parameters.get("th_chemo_check_no", None):
            sort_df("op_date_Surgery3 != ''")
            sort_df("th_previous_chemotherapy == 0")
        if parameters["th_previous_chemotherapy_cycles_von"]:
            para = int(parameters['th_previous_chemotherapy_cycles_von'])
            sort_df("th_previous_chemotherapy_cycles >= @para")
        if parameters["th_previous_chemotherapy_cycles_bis"]:
            para = int(parameters['th_previous_chemotherapy_cycles_bis'])
            sort_df("th_previous_chemotherapy_cycles <= @para")
        if parameters["th_previous_chemotherapy_type"]:
            para = parameters['th_previous_chemotherapy_type']
            sort_df("th_previous_chemotherapy_type == @para")
        if parameters["th_previous_antibody"]:
            para= parameters['th_previous_antibody']
            sort_df("th_previous_antibody == @para")

    # Check for PVE
    if parameters.get("PVECheck", None):
        if parameters.get("PVE_check_yes", None):
            sort_df("pve == True")
        if parameters.get("PVE_check_no", None):
            sort_df("pve == False")

    # Check for First OPs 

    if parameters.get("FirstOP_Check", None):
        if Mode:
            df_AND = df_AND[df_AND['op_date_Surgery1'].notnull()]
        sort_df("op_date_Surgery1 != ''")
        sort_df("op_date_Surgery2 == ''")
        sort_df("op_date_Surgery3 == ''")
    # Check for Second Ops
    if parameters.get("secondOP_Check", None):
        if Mode:
            df_AND = df_AND[df_AND['op_date_Surgery2'].notnull()]
        sort_df("op_date_Surgery2 != ''")
    # Check for First Ops
    if parameters.get("thirdOP_Check", None):
        if Mode:
            df_AND = df_AND[df_AND['op_date_Surgery3'].notnull()]
        sort_df("op_date_Surgery3 != ''")

    # Check for Limax Initial + Date
    if parameters.get("limax_initial_von", None):
        para = parameters['limax_initial_von']
        df["limax_initial"] = df["limax_initial"].dropna()
        sort_df("limax_initial >= @para")
    if parameters.get("limax_initial_bis", None):
        para = parameters['limax_initial_bis']
        df["limax_initial"] = df["limax_initial"].dropna()
        sort_df("limax_initial <= @para")
    if parameters.get('limax_initial_date_von', None):
        von_date = datetime.datetime.strptime(parameters['limax_initial_date_von'], constants.DATEFORMAT)
        von_date = datetime.date(von_date.year, von_date.month, von_date.day)
        sort_df("limax_initial_date >= @von_date")
    if parameters.get('limax_initial_date_bis', None):
        bis_date = datetime.datetime.strptime(parameters['limax_initial_date_bis'], constants.DATEFORMAT)
        bis_date = datetime.date(bis_date.year, bis_date.month, bis_date.day)
        sort_df("limax_initial_date <= @bis_date")

    # Check for Limax Second + Date

    if parameters.get("limax_second_von", None):
        para = int(parameters['limax_second_von'])
        sort_df("limax_second >= @para")
    if parameters.get("limax_second_bis", None):
        para = int(parameters['limax_second_bis'])
        sort_df("limax_second <= @para")
    if parameters.get('limax_second_date_von', None):
        von_date = datetime.datetime.strptime(parameters['limax_second_date_von'], constants.DATEFORMAT)
        von_date = datetime.date(von_date.year, von_date.month, von_date.day) 
        sort_df("limax_second_date >= @von_date")
    if parameters.get('limax_second_date_bis', None):
        bis_date = datetime.datetime.strptime(parameters['limax_second_date_bis'], constants.DATEFORMAT)
        bis_date = datetime.date(bis_date.year, bis_date.month, bis_date.day)
        sort_df("limax_second_date <= @bis_date")

    # Check for Limax Third + Date

    if parameters.get("limax_third_von", None):
        para = int(parameters['limax_third_von'])
        sort_df("limax_third >= @para")
    if parameters.get("limax_third_bis", None):
        para = int(parameters['limax_third_bis'])
        sort_df("limax_third <= @para")
    if parameters.get('limax_third_date_von', None):
        von_date = datetime.datetime.strptime(parameters['limax_third_date_von'], constants.DATEFORMAT)
        von_date = datetime.date(von_date.year, von_date.month, von_date.day)
        sort_df("limax_third_date >= @von_date")
    if parameters.get('limax_third_date_bis', None):
        bis_date = datetime.datetime.strptime(parameters['limax_third_date_bis'], constants.DATEFORMAT)
        bis_date = datetime.date(bis_date.year, bis_date.month, bis_date.day)
        sort_df("limax_third_date <= @bis_date")

    # Check for First OP Parameters Date

    if parameters.get("op_date_Surgery1_von", None) or parameters.get("op_date_Surgery1_bis", None) :
        if parameters.get('op_date_Surgery1_von', None):
            von_date = datetime.datetime.strptime(parameters['op_date_Surgery1_von'], constants.DATEFORMAT)
            von_date = datetime.date(von_date.year, von_date.month, von_date.day)
            sort_df("op_date_Surgery1 >= @von_date")
        if parameters.get('op_date_Surgery1_bis', None):
            bis_date = datetime.datetime.strptime(parameters['op_date_Surgery1_bis'], constants.DATEFORMAT)
            bis_date = datetime.date(bis_date.year, bis_date.month, bis_date.day)
            sort_df("op_date_Surgery1 <= @bis_date")

    # Check for First Op Code
    if parameters.get("op_code_Surgery1_checkbox", None):
        if parameters['op_code_Surgery1']:
            para =  parameters['op_code_Surgery1']
            sort_df("op_code_Surgery1 == @para")

    # Check for First OP Diagnosis
    if parameters.get("op_diagnosis_Surgery1_checkbox", None):
        if parameters['op_diagnosis_Surgery1']:
            para = parameters['op_diagnosis_Surgery1']
            sort_df("op_diagnosis_Surgery1 == @para")

    # Check for OP Methode
    if parameters.get('op_method_checkbox', None):
        paralist = []
        if parameters.get('checkoffen', None): paralist.append('offen')
        if parameters.get('checklaparoskopisch', None): paralist.append('laparoskopisch')
        if parameters.get('checkrobo', None): paralist.append('robotisch')
        sort_df("first_surgery_minimal_invasive in @paralist")

    # Check for OP Konversion
    if parameters.get('op1_conversion_checkbox', None):
        if parameters.get('op1_conversion_yes', None):
            sort_df("first_surgery_conversion == 1")
        if parameters.get('op1_conversion_no', None):
            sort_df("first_surgery_conversion == 0")
    
    if parameters.get('op1_ablation_checkbox', None):
        if parameters.get('op1_ablation_yes', None):
            sort_df("first_surgery_ablation == 1")
        if parameters.get('op1_ablation_no', None):
            sort_df("first_surgery_ablation == 0")

    # Check for Length
    if parameters.get("op_length_checkbox", None):
        if parameters.get("first_surgery_length_von",None):

            para = int(parameters['first_surgery_length_von'])
            sort_df("first_surgery_length >= @para")
        if parameters.get("first_surgery_length_bis"):
            para = int(parameters['first_surgery_length_bis'])
            sort_df("first_surgery_length <= @para")

    # Check for INtensivzeit
    if parameters.get("fs_icu_checkbox", None):
        df = df.dropna(subset=["op_date_Surgery1"])
        if parameters["fs_icu_von"]:
            para = int(parameters['fs_icu_von'])
            sort_df("fs_icu >= @para")
        if parameters["fs_icu_bis"]:
            para = int(parameters['fs_icu_bis'])
            sort_df("fs_icu <= @para")

    #  Check for LOS
    if parameters.get("fs_los_checkbox", None):
        if parameters["fs_los_von"]:
            para = int(parameters['fs_los_von'])
            sort_df("fs_los >= @para")
        if parameters["fs_los_bis"]:
            para = int(parameters['fs_los_bis'])
            sort_df("fs_los <= @para")

    # Check for DINDO
    if parameters.get('fs_dindo_checkbox', None):
        sort_df("op_date_Surgery1 != ''")
        paralist = []
        if parameters.get('fs_check_dindo_0', None):
            paralist.append('No comp')
        if parameters.get('fs_check_dindo_1', None):
            paralist.append('1')
        if parameters.get('fs_check_dindo_2', None):
            paralist.append('2')
        if parameters.get('fs_check_dindo_3a', None):
            paralist.append('3a')
        if parameters.get('fs_check_dindo_3b', None):
            paralist.append('3b')
        if parameters.get('fs_check_dindo_4a', None):
            paralist.append('4a')
        if parameters.get('fs_check_dindo_4b', None):
            paralist.append('4b')
        if parameters.get('fs_check_dindo_5', None):
            paralist.append('5')
        sort_df("fs_dindo in @paralist")

    # Check for Laborparameters first OP

    # #check for SerumBili fs

    # # Check for POD1
    if parameters.get("fs_serum_bili_pod1_checkbox", None):
        if parameters["fs_Serum_Bili_POD1_von"]:
            para = float(parameters['fs_Serum_Bili_POD1_von'])
            sort_df("fs_Serum_Bili_POD1 >= @para")
        if parameters["fs_Serum_Bili_POD1_bis"]:
            para = float(parameters['fs_Serum_Bili_POD1_bis'])
            sort_df("fs_Serum_Bili_POD1 <= @para")

    # # Check for POD3
    if parameters.get("fs_serum_bili_pod3_checkbox", None):
        if parameters["fs_Serum_Bili_POD3_von"]:
            para = float(parameters['fs_Serum_Bili_POD3_von'])
            sort_df("fs_Serum_Bili_POD3 >= @para")
        if parameters["fs_Serum_Bili_POD3_bis"]:
            para = float(parameters['fs_Serum_Bili_POD3_bis'])
            sort_df("fs_Serum_Bili_POD3 <= @para")

    # # Check for POD5
    if parameters.get("fs_serum_bili_pod5_checkbox", None):
        if parameters["fs_Serum_Bili_POD5_von"]:
            para = float(parameters['fs_Serum_Bili_POD5_von'])
            sort_df("fs_Serum_Bili_POD5 >= @para")
        if parameters["fs_Serum_Bili_POD5_bis"]:
            para = float(parameters['fs_Serum_Bili_POD5_bis'])
            sort_df("fs_Serum_Bili_POD5 <= @para")

    # # Check for Last
    if parameters.get("fs_serum_bili_last_checkbox", None):
        if parameters["fs_Serum_Bili_last_von"]:
            para = float(parameters['fs_Serum_Bili_last_von'])
            sort_df("fs_Serum_Bili_Last >= @para")
        if parameters["fs_Serum_Bili_last_bis"]:
            para = float(parameters['fs_Serum_Bili_last_bis'])
            sort_df("fs_Serum_Bili_Last <= @para")

    # #check for Drain Bili fs

    # # Check for POD1
    if parameters.get("fs_drain_bili_pod1_checkbox", None):
        if parameters.get("fs_drain_Bili_POD1_von",None):
            para = float(parameters['fs_drain_Bili_POD1_von'])
            sort_df("fs_Drain_Bili_POD1 >= @para")
        if parameters.get("fs_drain_Bili_POD1_bis",None):
            para = float(parameters['fs_drain_Bili_POD1_bis'])
            sort_df("fs_Drain_Bili_POD1 <= @para")

    # # Check for POD3
    if parameters.get("fs_drain_bili_pod3_checkbox", None):
        if parameters.get("fs_drain_Bili_pod3_von",None):
            para = float(parameters['fs_drain_Bili_pod3_von'])
            sort_df("fs_Drain_Bili_POD3 >= @para")
        if parameters.get("fs_drain_Bili_pod3_bis",None):
            para = float(parameters['fs_drain_Bili_pod3_bis'])
            sort_df("fs_Drain_Bili_POD3 <= @para")

    # # Check for POD5
    if parameters.get("fs_drain_bili_pod5_checkbox", None):
        if parameters["fs_drain_Bili_pod5_von"]:
            para = float(parameters['fs_drain_Bili_pod5_von'])
            sort_df("fs_Drain_Bili_POD5 >= @para")
        if parameters["fs_drain_Bili_pod5_bis"]:
            para = float(parameters['fs_drain_Bili_pod5_bis'])
            sort_df("fs_Drain_Bili_POD5 <= @para")

    # # Check for Last
    if parameters.get("fs_drain_bili_last_checkbox", None):
        if parameters["fs_drain_Bili_last_von"]:
            para = float(parameters['fs_drain_Bili_last_von'])
            sort_df("fs_Drain_Bili_Last >= @para")
        if parameters["fs_drain_Bili_last_bis"]:
            para = float(parameters['fs_drain_Bili_last_bis'])
            sort_df("fs_Drain_Bili_Last <= @para")

    # #Check for AST
    # # Check for POD1
    if parameters.get("fs_AST_POD1_checkbox", None):
        if parameters["fs_AST_POD1_von"]:
            para = int(parameters['fs_AST_POD1_von'])
            sort_df("fs_AST_POD1 >= @para")
        if parameters["fs_AST_POD1_bis"]:
            para = int(parameters['fs_AST_POD1_bis'])
            sort_df("fs_AST_POD1 <= @para")

    # # Check for POD3
    if parameters.get("fs_AST_POD3_checkbox", None):
        if parameters["fs_AST_POD3_von"]:
            para = int(parameters['fs_AST_POD3_von'])
            sort_df("fs_AST_POD3 >= @para")
        if parameters["fs_AST_POD3_bis"]:
            para = int(parameters['fs_AST_POD3_bis'])
            sort_df("fs_AST_POD3 <= @para")

    # # Check for POD5
    if parameters.get("fs_AST_POD5_checkbox", None):
        if parameters.get("fs_AST_POD5_von",None):
            para = int(parameters['fs_AST_POD5_von'])
            sort_df("fs_AST_POD5 >= @para")
        if parameters.get("fs_AST_POD5_bis",None):
            para = int(parameters['fs_AST_POD5_bis'])
            sort_df("fs_AST_POD5 <= @para")

    # # Check for Last
    if parameters.get("fs_AST_Last_checkbox", None):
        if parameters["fs_AST_Last_von"]:
            para = int(parameters['fs_AST_Last_von'])
            sort_df("fs_AST_Last >= @para")
        if parameters["fs_AST_Last_bis"]:
            para = int(parameters['fs_AST_Last_bis'])
            sort_df("fs_AST_Last <= @para")

    # #Check for ALT fs
    # # Check for POD1
    if parameters.get("fs_ALT_POD1_checkbox", None):
        if parameters.get("fs_ALT_POD1_von"):
            para = int(parameters['fs_ALT_POD1_von'])
            sort_df("fs_ALT_POD1 >= @para")
        if parameters.get("fs_ALT_POD1_bis",None):
            para = int(parameters['fs_ALT_POD1_bis'])
            sort_df("fs_ALT_POD1 <= @para")

    # # Check for POD3
    if parameters.get("fs_ALT_POD3_checkbox", None):
        if parameters["fs_ALT_POD3_von"]:
            para = int(parameters['fs_ALT_POD3_von'])
            sort_df("fs_ALT_POD3 >= @para")
        if parameters["fs_ALT_POD3_bis"]:
            para = int(parameters['fs_ALT_POD3_bis'])
            sort_df("fs_ALT_POD3 <= @para")

    # # Check for POD5
    if parameters.get("fs_ALT_pod5_checkbox", None):
        if parameters["fs_ALT_pod5_von"]:
            para = int(parameters['fs_ALT_pod5_von'])
            sort_df("fs_ALT_POD5 >= @para")
        if parameters["fs_ALT_pod5_bis"]:
            para = int(parameters['fs_ALT_pod5_bis'])
            sort_df("fs_ALT_POD5 <= @para")

    # # Check for Last
    if parameters.get("fs_ALT_Last_checkbox", None):
        if parameters["fs_ALT_Last_von"]:
            para = int(parameters['fs_ALT_Last_von'])
            sort_df("fs_ALT_Last >= @para")
        if parameters["fs_ALT_Last_bis"]:
            para = int(parameters['fs_ALT_Last_bis'])
            sort_df("fs_ALT_Last <= @para")

    # #Check for INR
    if parameters.get("fs_INR_POD1_checkbox", None):
        if parameters["fs_INR_POD1_von"]:
            para = float(parameters['fs_INR_POD1_von'])
            sort_df("fs_INR_POD1 >= @para")
        if parameters["fs_INR_POD1_bis"]:
            para = float(parameters['fs_INR_POD1_bis'])
            sort_df("fs_INR_POD1 <= @para")

    # # Check for POD3
    if parameters.get("fs_INR_POD3_checkbox", None):
        if parameters["fs_INR_POD3_von"]:
            para = float(parameters['fs_INR_POD3_von'])
            sort_df("fs_INR_POD3 >= @para")
        if parameters["fs_INR_POD3_bis"]:
            para = float(parameters['fs_INR_POD3_bis'])
            sort_df("fs_INR_POD3 <= @para")

    # # Check for POD5
    if parameters.get("fs_INR_pod5_checkbox", None):
        if parameters["fs_INR_pod5_von"]:
            para = float(parameters['fs_INR_pod5_von'])
            sort_df("fs_INR_POD5 >= @para")
        if parameters["fs_INR_pod5_bis"]:
            para = float(parameters['fs_INR_pod5_bis'])
            sort_df("fs_INR_POD5 <= @para")

    # # Check for Last
    if parameters.get("fs_INR_Last_checkbox", None):
        if parameters["fs_INR_Last_von"]:
            para = float(parameters['fs_INR_Last_von'])
            sort_df("fs_INR_Last >= @para")
        if parameters["fs_INR_Last_bis"]:
            para = float(parameters['fs_INR_Last_bis'])
            sort_df("fs_INR_Last <= @para")
    
    #Second OP 
    if parameters.get("second_surgery_planned_yes", None) or parameters.get("second_surgery_planned_no", None):
        df = df.dropna(subset=["second_surgery_planned"])
        if parameters.get('second_surgery_planned_yes', None):
            sort_df("second_surgery_planned == True")
        if parameters.get('second_surgery_planned_no', None):
            sort_df("second_surgery_planned == False")

    if parameters.get("second_surgery_realized_yes", None) or parameters.get("second_surgery_realized_no", None):
        df = df.dropna(subset=["second_surgery_realized"])
        if parameters.get('second_surgery_realized_yes', None):
            sort_df("second_surgery_realized == True")
        if parameters.get('second_surgery_realized_no', None):
            sort_df("second_surgery_realized == False")

    # Second OP Data
    if parameters.get("op_date_Surgery2_von", None) or parameters.get("op_date_Surgery2_bis", None) :
        if parameters.get('op_date_Surgery2_von', None):
            von_date = datetime.datetime.strptime(parameters['op_date_Surgery2_von'], constants.DATEFORMAT)
            von_date = datetime.date(von_date.year, von_date.month, von_date.day)
            sort_df("op_date_Surgery2 >= @von_date")
        if parameters.get('op_date_Surgery2_bis', None):
            bis_date = datetime.datetime.strptime(parameters['op_date_Surgery2_bis'], constants.DATEFORMAT)
            bis_date = datetime.date(bis_date.year, bis_date.month, bis_date.day)
            sort_df("op_date_Surgery2 <= @bis_date")


    # Check for Second Op Code
    if parameters.get("op_code_Surgery2_checkbox", None):
        if parameters['op_code_Surgery2']:
            para = parameters['op_code_Surgery2']
            sort_df("op_code_Surgery2 == @para")

    # Check for Second OP Diagnosis
    if parameters.get("op_diagnosis_Surgery2_checkbox", None):
        if parameters['op_diagnosis_Surgery2']:
            para= parameters['op_diagnosis_Surgery2']
            sort_df("op_diagnosis_Surgery2 == @para")


    # Check for OP Methode
    if parameters.get('ss_op_method_checkbox', None):
        paralist = []
        if parameters.get('ss_checkoffen', None): paralist.append('offen')
        if parameters.get('ss_checklaparoskopisch', None): paralist.append('laparoskopisch')
        if parameters.get('ss_checkrobo', None): paralist.append('robotisch')
        sort_df("second_surgery_minimal_invasive in @paralist")

    # Check for OP Konversion
    if parameters.get('op2_conversion_checkbox', None):
        if parameters.get('op2_conversion_yes', None):
            sort_df("second_surgery_conversion == True")
        if parameters.get('op2_conversion_no', None):
            sort_df("second_surgery_conversion == False")
    
    if parameters.get('op2ablation_checkbox', None):
        if parameters.get('op2_ablation_yes', None):
            sort_df("second_surgery_ablation == 1")
        if parameters.get('op2_ablation_no', None):
            sort_df("second_surgery_ablation == 0")

    # Check for Length
    if parameters.get("ss_op_length_checkbox", None):
        if parameters["second_surgery_length_von"]:
            para = int(parameters['second_surgery_length_von'])
            sort_df("second_surgery_length >= @para")
        if parameters["second_surgery_length_bis"]:
            para = int(parameters['second_surgery_length_bis'])
            sort_df("second_surgery_length <= @para")

    # Check for INtensivzeit
    if parameters.get("ss_icu_checkbox", None):
        df = df.dropna(subset=["op_date_Surgery2"])
        if parameters["ss_icu_von"]:
            para = int(parameters['ss_icu_von'])
            sort_df("ss_icu >= @para")
        if parameters["ss_icu_bis"]:
            para = int(parameters['ss_icu_bis'])
            sort_df("ss_icu <= @para")

    #  Check for LOS
    if parameters.get("ss_los_checkbox", None):
        if parameters["ss_los_von"]:
            para = int(parameters['ss_los_von'])
            sort_df("ss_los >= @para")
        if parameters["ss_los_bis"]:
            para = int(parameters['ss_los_bis'])
            sort_df("ss_los <= @para")

    # Check for DINDO
    if parameters.get('ss_dindo_checkbox', None):
        sort_df("op_date_Surgery2 != ''")
        paralist = []
        if parameters.get('ss_check_dindo_0', None): paralist.append('No comp'); paralist.append('No comp')
        if parameters.get('ss_check_dindo_1', None): paralist.append('I')
        if parameters.get('ss_check_dindo_2', None): paralist.append('II')
        if parameters.get('ss_check_dindo_3a', None): paralist.append('IIIa')
        if parameters.get('ss_check_dindo_3b', None): paralist.append('IIIb')
        if parameters.get('ss_check_dindo_4a', None): paralist.append('IVa')
        if parameters.get('ss_check_dindo_4b', None): paralist.append('IVb')
        if parameters.get('ss_check_dindo_5', None): paralist.append('V')
        sort_df("ss_dindo in @paralist")

    # Check for Laborparameters Second OP

    # #check for SerumBili ss

    # # Check for POD1
    if parameters.get("ss_serum_bili_pod1_checkbox", None):
        if parameters["ss_Serum_Bili_POD1_von"]:
            para = float(parameters['ss_Serum_Bili_POD1_von'])
            sort_df("ss_Serum_Bili_POD1 >= @para")
        if parameters["ss_Serum_Bili_POD1_bis"]:
            para = float(parameters['ss_Serum_Bili_POD1_bis'])
            sort_df("ss_Serum_Bili_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ss_serum_bili_pod3_checkbox", None):
        if parameters["ss_Serum_Bili_POD3_von"]:
            para = float(parameters['ss_Serum_Bili_POD3_von'])
            sort_df("ss_Serum_Bili_POD3 >= @para")
        if parameters["ss_Serum_Bili_POD3_bis"]:
            para = float(parameters['ss_Serum_Bili_POD3_bis'])
            sort_df("ss_Serum_Bili_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ss_serum_bili_pod5_checkbox", None):
        if parameters["ss_Serum_Bili_POD5_von"]:
            para = float(parameters['ss_Serum_Bili_POD5_von'])
            sort_df("ss_Serum_Bili_POD5 >= @para")
        if parameters["ss_Serum_Bili_POD5_bis"]:
            para = float(parameters['ss_Serum_Bili_POD5_bis'])
            sort_df("ss_Serum_Bili_POD5 <= @para")

    # # Check for Last
    if parameters.get("ss_serum_bili_last_checkbox", None):
        if parameters["ss_Serum_Bili_last_von"]:
            para = float(parameters['ss_Serum_Bili_last_von'])
            sort_df("ss_Serum_Bili_Last >= @para")
        if parameters["ss_Serum_Bili_last_bis"]:
            para = float(parameters['ss_Serum_Bili_last_bis'])
            sort_df("ss_Serum_Bili_Last <= @para")

    # #check for Drain Bili ss

    # # Check for POD1
    if parameters.get("ss_drain_bili_pod1_checkbox", None):
        if parameters["ss_drain_Bili_POD1_von"]:
            para = float(parameters['ss_drain_Bili_POD1_von'])
            sort_df("ss_Drain_Bili_POD1 >= @para")
        if parameters["ss_drain_Bili_POD1_bis"]:
            para = float(parameters['ss_drain_Bili_POD1_bis'])
            sort_df("ss_Drain_Bili_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ss_drain_bili_pod3_checkbox", None):
        if parameters["ss_drain_Bili_pod3_von"]:
            para = float(parameters['ss_drain_Bili_pod3_von'])
            sort_df("ss_Drain_Bili_POD3 >= @para")
        if parameters["ss_drain_Bili_pod3_bis"]:
            para = float(parameters['ss_drain_Bili_pod3_bis'])
            sort_df("ss_Drain_Bili_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ss_drain_bili_pod5_checkbox", None):
        if parameters["ss_drain_Bili_pod5_von"]:
            para = float(parameters['ss_drain_Bili_pod5_von'])
            sort_df("ss_Drain_Bili_POD5 >= @para")
        if parameters["ss_drain_Bili_pod5_bis"]:
            para = float(parameters['ss_drain_Bili_pod5_bis'])
            sort_df("ss_Drain_Bili_POD5 <= @para")

    # # Check for Last
    if parameters.get("ss_drain_bili_last_checkbox", None):
        if parameters["ss_drain_Bili_last_von"]:
            para = int(parameters['ss_drain_Bili_last_von'])
            sort_df("ss_Drain_Bili_Last >= @para")
        if parameters["ss_drain_Bili_last_bis"]:
            para = int(parameters['ss_drain_Bili_last_bis'])
            sort_df("ss_Drain_Bili_Last <= @para")

    # #Check for AST
    # # Check for POD1
    if parameters.get("ss_AST_POD1_checkbox", None):
        if parameters["ss_AST_POD1_von"]:
            para = int(parameters['ss_AST_POD1_von'])
            sort_df("ss_AST_POD1 >= @para")
        if parameters["ss_AST_POD1_bis"]:
            para = int(parameters['ss_AST_POD1_bis'])
            sort_df("ss_AST_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ss_AST_POD3_checkbox", None):
        if parameters["ss_AST_POD3_von"]:
            para = int(parameters['ss_AST_POD3_von'])
            sort_df("ss_AST_POD3 >= @para")
        if parameters["ss_AST_POD3_bis"]:
            para = int(parameters['ss_AST_POD3_bis'])
            sort_df("ss_AST_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ss_AST_pod5_checkbox", None):
        if parameters["ss_AST_pod5_von"]:
            para = int(parameters['ss_AST_pod5_von'])
            sort_df("ss_AST_POD5 >= @para")
        if parameters["ss_AST_pod5_bis"]:
            para = int(parameters['ss_AST_pod5_bis'])
            sort_df("ss_AST_POD5 <= @para")

    # # Check for Last
    if parameters.get("ss_AST_Last_checkbox", None):
        if parameters["ss_AST_Last_von"]:
            para = int(parameters['ss_AST_Last_von'])
            sort_df("ss_AST_Last >= @para")
        if parameters["ss_AST_Last_bis"]:
            para = int(parameters['ss_AST_Last_bis'])
            sort_df("ss_AST_Last <= @para")

    # #Check for ALT ss
    # # Check for POD1
    if parameters.get("ss_ALT_POD1_checkbox", None):
        if parameters["ss_ALT_POD1_von"]:
            para = int(parameters['ss_ALT_POD1_von'])
            sort_df("ss_ALT_POD1 >= @para")
        if parameters["ss_ALT_POD1_bis"]:
            para = int(parameters['ss_ALT_POD1_bis'])
            sort_df("ss_ALT_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ss_ALT_POD3_checkbox", None):
        if parameters["ss_ALT_POD3_von"]:
            para = int(parameters['ss_ALT_POD3_von'])
            sort_df("ss_ALT_POD3 >= @para")
        if parameters["ss_ALT_POD3_bis"]:
            para = int(parameters['ss_ALT_POD3_bis'])
            sort_df("ss_ALT_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ss_ALT_pod5_checkbox", None):
        if parameters["ss_ALT_pod5_von"]:
            para = int(parameters['ss_ALT_pod5_von'])
            sort_df("ss_ALT_POD5 >= @para")
        if parameters["ss_ALT_pod5_bis"]:
            para = int(parameters['ss_ALT_pod5_bis'])
            sort_df("ss_ALT_POD5 <= @para")

    # # Check for Last
    if parameters.get("ss_ALT_Last_checkbox", None):
        if parameters["ss_ALT_Last_von"]:
            para = int(parameters['ss_ALT_Last_von'])
            sort_df("ss_ALT_Last >= @para")
        if parameters["ss_ALT_Last_bis"]:
            para = int(parameters['ss_ALT_Last_bis'])
            sort_df("ss_ALT_Last <= @para")

    # #Check for INR
    if parameters.get("ss_INR_POD1_checkbox", None):
        if parameters["ss_INR_POD1_von"]:
            para = float(parameters['ss_INR_POD1_von'])
            sort_df("ss_INR_POD1 >= @para")
        if parameters["ss_INR_POD1_bis"]:
            para = float(parameters['ss_INR_POD1_bis'])
            sort_df("ss_INR_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ss_INR_POD3_checkbox", None):
        if parameters["ss_INR_POD3_von"]:
            para = float(parameters['ss_INR_POD3_von'])
            sort_df("ss_INR_POD3 >= @para")
        if parameters["ss_INR_POD3_bis"]:
            para = float(parameters['ss_INR_POD3_bis'])
            sort_df("ss_INR_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ss_INR_pod5_checkbox", None):
        if parameters["ss_INR_pod5_von"]:
            para = float(parameters['ss_INR_pod5_von'])
            sort_df("ss_INR_POD5 >= @para")
        if parameters["ss_INR_pod5_bis"]:
            para = float(parameters['ss_INR_pod5_bis'])
            sort_df("ss_INR_POD5 <= @para")

    # # Check for Last
    if parameters.get("ss_INR_Last_checkbox", None):
        if parameters["ss_INR_Last_von"]:
            para = float(parameters['ss_INR_Last_von'])
            sort_df("ss_INR_Last >= @para")
        if parameters["ss_INR_Last_bis"]:
            para = float(parameters['ss_INR_Last_bis'])
            sort_df("ss_INR_Last <= @para")

    # Third Op Data
    if parameters.get("third_surgery_planned_yes", None) or parameters.get("third_surgery_planned_no", None):
        df = df.dropna(subset=["third_surgery_planned"])
        if parameters.get('third_surgery_planned_yes', None):
            sort_df("third_surgery_planned == True")
        if parameters.get('third_surgery_planned_no', None):
            sort_df("third_surgery_planned == False")

    if parameters.get("third_surgery_realized_yes", None) or parameters.get("third_surgery_realized_no", None):
        df = df.dropna(subset=["third_surgery_realized"])
        if parameters.get('third_surgery_realized_yes', None):
            sort_df("third_surgery_realized == True")
        if parameters.get('third_surgery_realized_no', None):
            sort_df("third_surgery_realized == False")


    if parameters.get('op_date_Surgery3_von', None) or parameters.get('op_date_Surgery3_bis', None):
        if parameters.get('op_date_Surgery3_von', None):
            von_date = datetime.datetime.strptime(parameters['op_date_Surgery3_von'], constants.DATEFORMAT)
            von_date = datetime.date(von_date.year, von_date.month, von_date.day)
            sort_df("op_date_Surgery3 >= @von_date")
        if parameters.get('op_date_Surgery3_bis', None):
            bis_date = datetime.datetime.strptime(parameters['op_date_Surgery3_bis'], constants.DATEFORMAT)
            bis_date = datetime.date(bis_date.year, bis_date.month, bis_date.day)
            sort_df("op_date_Surgery3 <= @bis_date")

    # Check for Second Op Code
    if parameters.get("op_code_Surgery3_checkbox", None):
        if parameters['op_code_Surgery3']:
            para = parameters['op_code_Surgery3']
            sort_df("op_code_Surgery3 == @para")

    # Check for Second OP Diagnosis
    if parameters.get("op_diagnosis_Surgery3_checkbox", None):
        if parameters['op_diagnosis_Surgery3']:
            para = parameters['op_diagnosis_Surgery3']
            sort_df("op_diagnosis_Surgery3 == @para")

    # Check for OP Methode
    if parameters.get('ts_op_method_checkbox', None):

        paralist = []
        if parameters.get('ts_checkoffen', None): paralist.append('offen')
        if parameters.get('ts_checklaparoskopisch', None): paralist.append('laparoskopisch')
        if parameters.get('ts_checkrobo', None): paralist.append('robotisch')
        sort_df("third_surgery_minimal_invasiv in @paralist")

    # Check for OP Konversion
    if parameters.get('op3_conversion_checkbox', None):
        if parameters.get('op3_conversion_yes', None):
            sort_df("third_surgery_conversion == 1")
        if parameters.get('op3_conversion_no', None):
            sort_df("third_surgery_conversion == 0")
    
    if parameters.get('op3_ablation_checkbox', None):
        if parameters.get('op3_ablation_yes', None):
            sort_df("third_surgery_ablation == 1")
        if parameters.get('op3_ablation_no', None):
            sort_df("third_surgery_ablation == 0")

    # Check for Length
    if parameters.get("ts_op_length_checkbox", None):
        if parameters["third_surgery_length_von"]:
            para = int(parameters['third_surgery_length_von'])
            sort_df("third_surgery_length >= @para")
        if parameters["third_surgery_length_bis"]:
            para = int(parameters['third_surgery_length_bis'])
            sort_df("third_surgery_length <= @para")

    # Check for INtensivzeit
    if parameters.get("ts_icu_checkbox", None):
        df = df.dropna(subset=["op_date_Surgery3"])
        if parameters["ts_icu_von"]:
            para = int(parameters['ts_icu_von'])
            sort_df("ts_icu >= @para")
        if parameters["ts_icu_bis"]:
            para = int(parameters['ts_icu_bis'])
            sort_df("ts_icu <= @para")

    #  Check for LOS
    if parameters.get("ts_los_checkbox", None):
        if parameters["ts_los_von"]:
            para = int(parameters['ts_los_von'])
            sort_df("th_los >= @para")
        if parameters["ts_los_bis"]:
            para = int(parameters['ts_los_bis'])
            sort_df("th_los <= @para")

    # Check for DINDO
    if parameters.get('ts_dindo_checkbox', None):
        sort_df("op_date_Surgery3 != ''")
        paralist = []
        if parameters.get('ts_check_dindo_0', None): paralist.append('No comp'); paralist.append('No comp')
        if parameters.get('ts_check_dindo_1', None): paralist.append('I')
        if parameters.get('ts_check_dindo_2', None): paralist.append('II')
        if parameters.get('ts_check_dindo_3a', None): paralist.append('IIIa')
        if parameters.get('ts_check_dindo_3b', None): paralist.append('IIIb')
        if parameters.get('ts_check_dindo_4a', None): paralist.append('IVa')
        if parameters.get('ts_check_dindo_4b', None): paralist.append('IVb')
        if parameters.get('ts_check_dindo_5', None): paralist.append('V')
        sort_df("ts_dindo in @paralist")

    # Check for Third OP Labor
    # Check for Laborparameters Second OP

    # #check for SerumBili ss

    # # Check for POD1
    if parameters.get("ts_serum_bili_pod1_checkbox", None):
        if parameters["ts_Serum_Bili_POD1_von"]:
            para = float(parameters['ts_Serum_Bili_POD1_von'])
            sort_df("ts_Serum_Bili_POD1 >= @para")
        if parameters["ts_Serum_Bili_POD1_bis"]:
            para = float(parameters['ts_Serum_Bili_POD1_bis'])
            sort_df("ts_Serum_Bili_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ts_serum_bili_pod3_checkbox", None):
        if parameters["ts_Serum_Bili_POD3_von"]:
            para = float(parameters['ts_Serum_Bili_POD3_von'])
            sort_df("ts_Serum_Bili_POD3 >= @para")
        if parameters["ts_Serum_Bili_POD3_bis"]:
            para = float(parameters['ts_Serum_Bili_POD3_bis'])
            sort_df("ts_Serum_Bili_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ts_serum_bili_pod5_checkbox", None):
        if parameters["ts_Serum_Bili_POD5_von"]:
            para = float(parameters['ts_Serum_Bili_POD5_von'])
            sort_df("ts_Serum_Bili_POD5 >= @para")
        if parameters["ts_Serum_Bili_POD5_bis"]:
            para = float(parameters['ts_Serum_Bili_POD5_bis'])
            sort_df("ts_Serum_Bili_POD5 <= @para")

    # # Check for Last
    if parameters.get("ts_serum_bili_last_checkbox", None):
        if parameters["ts_Serum_Bili_last_von"]:
            para = float(parameters['ts_Serum_Bili_last_von'])
            sort_df("ts_Serum_Bili_Last >= @para")
        if parameters["ts_Serum_Bili_last_bis"]:
            para = float(parameters['ts_Serum_Bili_last_bis'])
            sort_df("ts_Serum_Bili_Last <= @para")

    # #check for Drain Bili ss

    # # Check for POD1
    if parameters.get("ts_drain_bili_pod1_checkbox", None):
        if parameters["ts_drain_Bili_POD1_von"]:
            para = float(parameters['ts_drain_Bili_POD1_von'])
            sort_df("ts_Drain_Bili_POD1 >= @para")
        if parameters["ts_drain_Bili_POD1_bis"]:
            para = float(parameters['ts_drain_Bili_POD1_bis'])
            sort_df("ts_Drain_Bili_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ts_drain_bili_pod3_checkbox", None):
        if parameters["ts_drain_Bili_pod3_von"]:
            para = float(parameters['ts_drain_Bili_pod3_von'])
            sort_df("ts_Drain_Bili_POD3 >= @para")
        if parameters["ts_drain_Bili_pod3_bis"]:
            para = float(parameters['ts_drain_Bili_pod3_bis'])
            sort_df("ts_Drain_Bili_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ts_drain_bili_pod5_checkbox", None):
        if parameters["ts_drain_Bili_pod5_von"]:
            para = float(parameters['ts_drain_Bili_pod5_von'])
            sort_df("ts_Drain_Bili_POD5 >= @para")
        if parameters["ts_drain_Bili_pod5_bis"]:
            para = float(parameters['ts_drain_Bili_pod5_bis'])
            sort_df("ts_Drain_Bili_POD5 <= @para")

    # # Check for Last
    if parameters.get("ts_drain_bili_last_checkbox", None):
        if parameters["ts_drain_Bili_last_von"]:
            para = float(parameters['ts_drain_Bili_last_von'])
            sort_df("ts_Drain_Bili_Last >= @para")
        if parameters["ts_drain_Bili_last_bis"]:
            para = float(parameters['ts_drain_Bili_last_bis'])
            sort_df("ts_Drain_Bili_Last <= @para")

    # #Check for AST
    # # Check for POD1
    if parameters.get("ts_AST_POD1_checkbox", None):
        if parameters["ts_AST_POD1_von"]:
            para = int(parameters['ts_AST_POD1_von'])
            sort_df("ts_AST_POD1 >= @para")
        if parameters["ts_AST_POD1_bis"]:
            para = int(parameters['ts_AST_POD1_bis'])
            sort_df("ts_AST_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ts_AST_POD3_checkbox", None):
        if parameters["ts_AST_POD3_von"]:
            para = int(parameters['ts_AST_POD3_von'])
            sort_df("ts_AST_POD3 >= @para")
        if parameters["ts_AST_POD3_bis"]:
            para = int(parameters['ts_AST_POD3_bis'])
            sort_df("ts_AST_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ts_AST_pod5_checkbox", None):
        if parameters["ts_AST_pod5_von"]:
            para = int(parameters['ts_AST_pod5_von'])
            sort_df("ts_AST_POD5 >= @para")
        if parameters["ts_AST_pod5_bis"]:
            para = int(parameters['ts_AST_pod5_bis'])
            sort_df("ts_AST_POD5 <= @para")

    # # Check for Last
    if parameters.get("ts_AST_Last_checkbox", None):
        if parameters["ts_AST_Last_von"]:
            para = int(parameters['ts_AST_Last_von'])
            sort_df("ts_AST_LAST >= @para")
        if parameters["ts_AST_Last_bis"]:
            para = int(parameters['ts_AST_Last_bis'])
            sort_df("ts_AST_LAST <= @para")

    # #Check for ALT ss
    # # Check for POD1
    if parameters.get("ts_ALT_POD1_checkbox", None):
        if parameters["ts_ALT_POD1_von"]:
            para = int(parameters['ts_ALT_POD1_von'])
            sort_df("ts_ALT_POD1 >= @para")
        if parameters["ts_ALT_POD1_bis"]:
            para = int(parameters['ts_ALT_POD1_bis'])
            sort_df("ts_ALT_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ts_ALT_POD3_checkbox", None):
        if parameters["ts_ALT_POD3_von"]:
            para = int(parameters['ts_ALT_POD3_von'])
            sort_df("ts_ALT_POD3 >= @para")
        if parameters["ts_ALT_POD3_bis"]:
            para = int(parameters['ts_ALT_POD3_bis'])
            sort_df("ts_ALT_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ts_ALT_pod5_checkbox", None):
        if parameters["ts_ALT_pod5_von"]:
            para = int(parameters['ts_ALT_pod5_von'])
            sort_df("ts_ALT_POD5 >= @para")
        if parameters["ts_ALT_pod5_bis"]:
            para = int(parameters['ts_ALT_pod5_bis'])
            sort_df("ts_ALT_POD5 <= @para")

    # # Check for Last
    if parameters.get("ts_ALT_Last_checkbox", None):
        if parameters["ts_ALT_Last_von"]:
            para = int(parameters['ts_ALT_Last_von'])
            sort_df("ts_ALT_Last >= @para")
        if parameters["ts_ALT_Last_bis"]:
            para = int(parameters['ts_ALT_Last_bis'])
            sort_df("ts_ALT_Last <= @para")

    # #Check for INR
    if parameters.get("ts_INR_POD1_checkbox", None):
        if parameters["ts_INR_POD1_von"]:
            para = float(parameters['ts_INR_POD1_von'])
            sort_df("ts_INR_POD1 >= @para")
        if parameters["ts_INR_POD1_bis"]:
            para = float(parameters['ts_INR_POD1_bis'])
            sort_df("ts_INR_POD1 <= @para")

    # # Check for POD3
    if parameters.get("ts_INR_POD3_checkbox", None):
        if parameters["ts_INR_POD3_von"]:
            para = float(parameters['ts_INR_POD3_von'])
            sort_df("ts_INR_POD3 >= @para")
        if parameters["ts_INR_POD3_bis"]:
            para = float(parameters['ts_INR_POD3_bis'])
            sort_df("ts_INR_POD3 <= @para")

    # # Check for POD5
    if parameters.get("ts_INR_pod5_checkbox", None):
        if parameters["ts_INR_pod5_von"]:
            para = float(parameters['ts_INR_pod5_von'])
            sort_df("ts_INR_POD5 >= @para")
        if parameters["ts_INR_pod5_bis"]:
            para = float(parameters['ts_INR_pod5_bis'])
            sort_df("ts_INR_POD5 <= @para")

    # # Check for Last
    if parameters.get("ts_INR_Last_checkbox", None):
        if parameters["ts_INR_Last_von"]:
            para = float(parameters['ts_INR_Last_von'])
            sort_df("ts_INR_Last >= @para")
        if parameters["ts_INR_Last_bis"]:
            para = float(parameters['ts_INR_Last_bis'])
            sort_df("ts_INR_Last <= @para")

    df.fillna("None")

    if Mode:
        
        return df_AND
    else:
        
        return df_or
