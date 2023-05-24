import codecs
import datetime

import flask
import jinja2
import matplotlib
import matplotlib.pyplot
import numpy
import pandas
import regex
import scipy
import statsmodels.api as sm
from flask_session import Session
import os


app = flask.Flask(__name__,
                  template_folder="templates",
                  static_folder="static")

api_key = os.environ.get("KRK_DB_API_KEY")
print(api_key)

api_secret = os.environ.get("KRK_DB_SECRET_KEY")

app.secret_key = os.environ.get("KRK_APP_SECRET_KEY")
app.config['SESSION_TYPE'] = 'filesystem'
app.config["JWT_SECRET_KEY"] = os.environ.get("KRK_APP_SECRET_KEY")
Session(app)

PATH_OUT = "./Calculated_Statistic/"

latex_jinja_env = jinja2.Environment(
    block_start_string='\BLOCK{',
    block_end_string='}',
    variable_start_string='\VAR{',
    variable_end_string='}',
    comment_start_string='\#{',
    comment_end_string='}',
    line_statement_prefix='%-',
    line_comment_prefix='%#',
    trim_blocks=True,
    autoescape=False,
    loader=jinja2.FileSystemLoader(os.path.abspath("."))
)

template = latex_jinja_env.get_template("stat_template.tex")

labor_verlauf_liste = []
op_nm = ""
labor_typ = ""



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
           "fs_previous_antibody",
           "ss_previous_antibody",
           "th_previous_antibody",
           

           ]

booleans = [
    "alcohol",
    "pve",
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
    "second_surgery_planned",
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
    # Laborwerte
    ##Erste OP
    "fs_Serum_Bili_POD1",
    "fs_Serum_Bili_POD3",
    "fs_Serum_Bili_POD5",
    "fs_Serum_Bili_Last",
    "fs_Drain_Bili_POD1",
    "fs_Drain_Bili_POD3",
    "fs_Drain_Bili_POD5",
    "fs_Drain_Bili_Last",
    "fs_AST_POD1",
    "fs_AST_POD3",
    "fs_AST_POD5",
    "fs_AST_Last",
    "fs_ALT_POD1",
    "fs_ALT_POD3",
    "fs_ALT_POD5",
    "fs_ALT_Last",
    "fs_INR_POD1",
    "fs_INR_POD3",
    "fs_INR_POD5",
    "fs_INR_Last",
    # Zweite OP
    "ss_Serum_Bili_POD1",
    "ss_Serum_Bili_POD3",
    "ss_Serum_Bili_POD5",
    "ss_Serum_Bili_Last",
    "ss_Drain_Bili_POD1",
    "ss_Drain_Bili_POD3",
    "ss_Drain_Bili_POD5",
    "ss_Drain_Bili_Last",
    "ss_AST_POD1",
    "ss_AST_POD3",
    "ss_AST_POD5",
    "ss_AST_Last",
    "ss_ALT_POD1",
    "ss_ALT_POD3",
    "ss_ALT_POD5",
    "ss_ALT_Last",
    "ss_INR_POD1",
    "ss_INR_POD3",
    "ss_INR_POD5",
    "ss_INR_Last",
    # Dritte OP
    "ts_Serum_Bili_POD1",
    "ts_Serum_Bili_POD3",
    "ts_Serum_Bili_POD5",
    "ts_Serum_Bili_Last",
    "ts_Drain_Bili_POD1",
    "ts_Drain_Bili_POD3",
    "ts_Drain_Bili_POD5",
    "ts_Drain_Bili_Last",
    "ts_AST_POD1",
    "ts_AST_POD3",
    "ts_AST_POD5",
    "ts_AST_Last",
    "ts_ALT_POD1",
    "ts_ALT_POD3",
    "ts_ALT_POD5",
    "ts_ALT_Last",
    "ts_INR_POD1",
    "ts_INR_POD3",
    "ts_INR_POD5",
    "ts_INR_Last",
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
    "th_los",
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
    "R",
    "first_surgery_minimal_invasive",
    "second_surgery_minimal_invasive",
    "third_surgery_minimal_invasiv"
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
    "dob",
]

labor_werte = [
    "fs_Serum_Bili_POD1",
    "fs_Serum_Bili_POD3",
    "fs_Serum_Bili_POD5",
    "fs_Serum_Bili_Last",
    "fs_Drain_Bili_POD1",
    "fs_Drain_Bili_POD3",
    "fs_Drain_Bili_POD5",
    "fs_Drain_Bili_Last",
    "fs_AST_POD1",
    "fs_AST_POD3",
    "fs_AST_POD5",
    "fs_AST_Last",
    "fs_ALT_POD1",
    "fs_ALT_POD3",
    "fs_ALT_POD5",
    "fs_ALT_Last",
    "fs_INR_POD1",
    "fs_INR_POD3",
    "fs_INR_POD5",
    "fs_INR_Last",
    # Zweite OP
    "ss_Serum_Bili_POD1",
    "ss_Serum_Bili_POD3",
    "ss_Serum_Bili_POD5",
    "ss_Serum_Bili_Last",
    "ss_Drain_Bili_POD1",
    "ss_Drain_Bili_POD3",
    "ss_Drain_Bili_POD5",
    "ss_Drain_Bili_Last",
    "ss_AST_POD1",
    "ss_AST_POD3",
    "ss_AST_POD5",
    "ss_AST_Last",
    "ss_ALT_POD1",
    "ss_ALT_POD3",
    "ss_ALT_POD5",
    "ss_ALT_Last",
    "ss_INR_POD1",
    "ss_INR_POD3",
    "ss_INR_POD5",
    "ss_INR_Last",
    # Dritte OP
    "th_Serum_Bili_POD1",
    "th_Serum_Bili_POD3",
    "th_Serum_Bili_POD5",
    "th_Serum_Bili_Last",
    "th_Drain_Bili_POD1",
    "th_Drain_Bili_POD3",
    "th_Drain_Bili_POD5",
    "th_Drain_Bili_Last",
    "th_AST_POD1",
    "th_AST_POD3",
    "th_AST_POD5",
    "th_AST_Last",
    "th_ALT_POD1",
    "th_ALT_POD3",
    "th_ALT_POD5",
    "th_ALT_Last",
    "th_INR_POD1",
    "th_INR_POD3",
    "th_INR_POD5",
    "th_INR_Last"
]

global result
status = 0
current_task = 0
max_task = 0

def update_max(max):
    global max_task
    max_task = max

def max():
    print("jetzt current update")
    global current_task
    current_task += 1
    global status 
    status = progress_bar(current_task, max_task)

def progress_bar(current_task, max_task):
    print("hier current")
    print(current_task)
    print("hier max")
    global status
    status = current_task/max_task
    print("hier status")
    print(status)
    return status




pandas.set_option('display.float_format', lambda x: '%.3f' % x)

#This function builds a dict for LaTeC to understand and render in a Table
def build_dict(datatype, data):
    if datatype not in ["Image", "Table"]:
        raise ValueError("Datatype didn't match Image or Table")
    flask.session["elements"].append({"type": datatype, "data": data})


def table_one_func(x, loesung):  #Formates result output into a list
    lista = [[x]]
    print(loesung.values)
    for i, j in zip(loesung.axes[0].values.astype(str), loesung.values.astype(str)):
        i = i.replace("%", "\\%")
        j = j.replace("%", "\\%")
        lista = lista + [[i, j]]

    x = x.replace("_", "-")
    lista[0] = [x, "..."]

    return lista


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        return '{p:.2f}%  ({v:d})'.format(p=pct, v=val)

    return my_autopct

def deskriptiv(df, points_of_interest, grafik, table_one):
   
    # Table one für Werte aus DF und Liste zur beschränkung der werte
    df = pandas.DataFrame(df)
    for x in points_of_interest:
        if x in to_drop:
            print("to_drop für" + x)
            max()
            continue
        
      
        current_name = x
        current_df = df[x]
        current_df.dropna(inplace=True)

        #Format input df for better functionality with statistical libaries
        if x in dates:
            print("in dates für" + x)
            max()
            continue

        if x in booleans:
            df = df.replace({0: False, 1: True})

        if x in decimals:
            current_df = pandas.to_numeric(current_df, errors='coerce')

        if x in categorials or x in ordinals:
            print("in cat or ordinals: " + x)
            current_df = current_df.astype(str)
            current_df[1] = current_df.replace("", numpy.nan, inplace=True)
            current_df[1] = current_df.dropna(inplace=True)
            print(current_df)
            


        #Generate table one if wanted
        if (table_one):
            result = current_df.describe()
            table = table_one_func(x, result)  # table is ne liste
            build_dict("Table", table)
            max()
            
            
        #Generate A Graph from Table One
        if (grafik):
               
            #Generate Graph as Cake Graph
            if x in booleans:
                values = current_df.value_counts()
                if len(values) >= 2:
                    val = ['False:', 'True:']
                    values = [values[0], values[1]]
                    series2 = pandas.Series(values,
                                            index=val,
                                            name=current_name + "(" + str(sum(values)) + ")")
                    pie = series2.plot.pie(figsize=(6, 6), autopct=make_autopct(values))
                    fig = pie.get_figure()
                    save_here = PATH_OUT + flask.session["username"] + "_" + x + "_kuchen.png"
                    fig.savefig(save_here)
                    build_dict("Image", flask.session["username"] + "_" + x + "_kuchen.png")
                    fig.clf()
                    values = None
                    series2 = None
            #Generate a Boxplot Graph 
            if x in decimals:
                pie = current_df.plot.box(figsize=(6, 6))
                fig = pie.get_figure()
                save_here = PATH_OUT + flask.session["username"] + "_" + x + "_box.png"
                fig.savefig(save_here)
                build_dict("Image", flask.session["username"] + "_" + x + "_box.png")
                fig.clf()
            #Generate A Balkendiagramm
            if x in categorials or x in ordinals:
                current_df = current_df.value_counts()
                print(current_df)
                pie = current_df.plot.bar(figsize=(6, 6))
                fig = pie.get_figure()
                save_here = PATH_OUT + flask.session["username"] + "_" + x + "_balken.png"
                fig.savefig(save_here)
                build_dict("Image", flask.session["username"] + "_" + x + "_balken.png")
                fig.clf()
            print("in grafik onefür" + x)
            max() 
           
            
            


def explorativ(df, points_of_interest, saphiro, kolmogorov, qqplot, histo,scat,scat_one,scat_two,scat_three):
   
    # Test auf Normalverteilung und entsprechender T-Test
    if (scat == True and scat_one and scat_two and scat_three):
        print("in scat")
        max()  
        print(scat_one)
        print(scat_two)
        print(scat_three)
        df = pandas.DataFrame(df)
        print(df)
        current_df = df
        listb= [scat_one,scat_two]
        if scat_three:
            listb.append(scat_three)
        
        listc = []
        for obj in listb:
            temp_df = current_df[obj]
            if obj in booleans:
                temp_df  = temp_df.replace({0: False, 1: True})
                temp_df.dropna(inplace=True)
                a1 = temp_df

            if obj in decimals:
                temp_df.dropna(inplace=True)
                temp_df[1] = temp_df.replace("", numpy.nan, inplace=True)
                temp_df = temp_df.astype(float)
                a1 = temp_df

            if obj in categorials:
                temp_df.dropna(inplace=True)
                temp_df = temp_df.astype(str)
                a1 = temp_df

            listc.append(a1)
            
        if len(listc) == 2: #and array3: 
                print("hier value1")
                value1 = listc[0]
                value1.dropna(inplace=True)
                value1 = value1.reset_index()
                value1 = value1[[scat_one]]
                value1 = value1.squeeze()
                print(value1)
                value2 = listc[1]
                value2.dropna(inplace=True)
                value2 = value2.reset_index()
                value2 = value2[[scat_two]]
                value2 = value2.squeeze()
                print(value2)

                n = len(value1)
                k = len(value2)

                print("n - k:")
                print (n - k)

                print("k - n:")
                print (k - n)

                print(type(value1))
                print(type(value2))

                if ((n - k) > 0):
                    for i in range(0, n - k ):
                        print("in pop v2")
                        print("das ist i: ")
                        print(i)
                        print(value1[i])
                        value1.pop(i)
                if((n - k)<0):
                    for i in range(0, k - n ):
                        print("in pop v1")
                        print("das ist i: ")
                        print(i)
                        value2.pop(i)

                print("len value1")
                print(value1)
                print(len(value1))
                print("len value2")
                print(value2)
                print(len(value2))

                print("in scatter plot")

                print("moin")
                scatter = matplotlib.pyplot.scatter(value1 ,value2)
                fig = scatter.get_figure()
                x = scat_one + " and " + scat_two
                save_here = PATH_OUT + flask.session["username"] + "_" + x + "_scat.png"
                fig.savefig(save_here)
                build_dict("Image", flask.session["username"] + "_" + x + "_scat.png")
                fig.clf()
        elif len(listc) == 3:
            print("in 3 len")
            if scat_three in booleans or scat_three in categorials:
                print("in scat_there")
                df_temp = df[[scat_one,scat_two,scat_three]]
                df_temp.dropna(inplace=True)
                valuelist = []
                for x in df_temp[scat_three].values:
                    if x not in valuelist:
                        valuelist.append(x)
                for x in valuelist:
                    mask = df_temp[scat_three] == x
                    a = df_temp[mask]
                    value1= a[a.columns[0]]
                    value2 = a[a.columns[1]]
                    fig = matplotlib.pyplot.scatter(value1 ,value2,label=x)

                matplotlib.pyplot.legend()
                fig= fig.get_figure()
                x = scat_one + " and " + scat_two
                save_here = PATH_OUT + flask.session["username"] + "_" + x + "_scat.png"
                fig.savefig(save_here)
                build_dict("Image", flask.session["username"] + "_" + x + "_scat.png")
                fig.clf()
        else:
                table = ([x, " :Scatterplott"], ["Fehler", "Bitte wähle mehr als einen Wert"])
                build_dict("Table", table)

        
    else:
            if scat == True:
                print("in kein scatter")
                max()  
            
        
        

    for x in points_of_interest:
        if x in decimals:
            df = pandas.DataFrame(df)
            print(df)
            # Vorbereitungen: Spalte rausziehen, zu numbern, leere spalten loswerden
            current_df = df[x]

            current_df = pandas.to_numeric(current_df, errors='coerce')

            current_df = current_df[~numpy.isnan(current_df)]

            if (saphiro == True):
                result = scipy.stats.shapiro(current_df)
                tt = round(result[0],3)
                pw = round(result[1],3)
                table = ([x.replace("_", "-"), " Saphiro-Wilkoson Test"], ["Teststatistik", tt], ["P-Wert", pw])
                build_dict("Table", table)
                print("in saphiro"+x) 
                max()
           
            if (kolmogorov == True):
                result = scipy.stats.kstest(current_df, 'norm')
                tt = round(result[0],3)
                pw = round(result[1],3)
                table = ([x.replace("_", "-"), " Kolmogorov-Smirnov Test"], ["Teststatistik", tt], ["P-Wert",pw])
                build_dict("Table", table)
                print("in kolmogrov"+x) 
                max()
            
            if (qqplot == True):
                
               
                with matplotlib.rc_context():
                    matplotlib.rc("figure", figsize=(6,6))
                    fig = sm.qqplot(current_df,scipy.stats.norm, fit= True, line='45', xlabel='Zu erwartende Werte', ylabel=x)
               
                save_here = PATH_OUT + x + "_qqplot.png"
                fig.savefig(save_here)
                build_dict("Image", x + "_qqplot.png")
                fig.clf()
                print("in qq"+x) 
                max()
            
            if (histo == True):
                
           
                print("hier histo")
                fig, ax = matplotlib.pyplot.subplots()
                current_df.plot.kde(ax=ax, legend=False)
                current_df.plot.hist(density=True, ax=ax, figsize=(6, 6))
                ax.set_ylabel('Probability')
                ax.grid(axis='y')
                ax.set_facecolor('#d8dcd6')
                save_here = PATH_OUT + flask.session["username"] + "_" + x + "_histo.png"
                fig.savefig(save_here)
                build_dict("Image", flask.session["username"] + "_" + x + "_histo.png")
                fig.clf()
                print("in histo" +x) 
                max()
            
        else:
                if saphiro:
                     max()
                if histo:
                     max()
                if qqplot:
                    max()
                if kolmogorov:
                    max()
            
        



    print("Wuhu, normalverteilt")


def stat_test(df, point_of_interest, reg_one, reg_two, linear, korrelation, ttest_v, ttest_unv, utest, will, mode_unv, mode_v, mode_u,mode_w):
    # Test / Darstellung von korrellation

    H0_x = "H0 verwerfen"
    H0_y= "H0 annehmen"
    
    def modus(mode):
        if mode == "zweizeitig":
            return "two-sided" 
        if mode == "links":
            return "less"
        if mode == "rechts":
            return "greater"

    def check_variable(variable):
        global bool_values
        global constans
        if len(bool_values) == 0 and variable in booleans:
            bool_values = df[reg_one]
            bool_values = pandas.get_dummies(bool_values, drop_first=True)
        if len(constans) == 0 and variable in decimals:
            constans = df[reg_one]
            constans = pandas.to_numeric(constans, errors='coerce')
            constans.dropna(inplace=True)

    df = pandas.DataFrame(df)
    labor_verlauf_liste = []
    

    def verlauf_check(x):
        if x in labor_werte:
            print("teste auf verlauf")
            global op_nm
            global labor_typ
            op_nm = x.split("_")[0]
            print(op_nm)
            labor_typ = x.split("_")[1]
            print(labor_typ)
            my_regex = regex.escape(op_nm) + regex.escape(labor_typ)
            for s in labor_verlauf_liste:
                print("in verlaufs schleife")
                if regex.search(my_regex, s):
                    print("its true, verlauf bereits angelegt")
                    return True
                else:
                    print('verlauf noch nicht angelegt')
                    labor_verlauf_liste.append(op_nm + labor_typ)
                    print(labor_verlauf_liste)
                    return False
            if not labor_verlauf_liste:
                print('verlauf noch nicht angelegt')
                labor_verlauf_liste.append(op_nm + labor_typ)
                print(labor_verlauf_liste)
                return False
        

    def lin_reg(row):
        print("linreg")
        ywerte = []
        xwerte = []
        print(row)
        row = pandas.to_numeric(row, errors='coerce')

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
        
        print(xwerte)
        print(ywerte)
        if len(xwerte) != 0 or len(ywerte) != 0:
            slope, intercept, r, p, se = scipy.stats.linregress(x=xwerte, y=ywerte, alternative='two-sided')
            return slope

    if linear:
        for x in point_of_interest:
            if x not in labor_werte:
                print("not in linear")
                max()
                continue

            if verlauf_check(x):
                max()
                continue
            # now we need to create a new dataframe with all of the Data in linearer regression zum vergleich
            print(op_nm)
            value = op_nm + "_"
            print(value)
            if (labor_typ == "Serum" or labor_typ == "Drain"):
                value = value + labor_typ + "_Bili"
            else:
                value = value + labor_typ
            valuepoint1 = value + '_POD1'
            valuepoint2 = value + '_POD3'
            valuepoint3 = value + '_POD5'
            valuepoint4 = value + '_Last'
            valuepoint5 = op_nm + "_los"

            df2 = df[[valuepoint1, valuepoint2, valuepoint3, valuepoint4, valuepoint5]]
            df2.dropna(axis=0, how="all", inplace=True)

            # BEGINN DER REGRESSION!
            df2['Slope'] = df2.apply(lin_reg, axis=1)
            print(df2)

            # Hier table One
            df3 = df2['Slope']
            df3 = pandas.to_numeric(df3, errors='coerce')

            result = df3.describe()
            round(result, 5)
            x =  value + "- Regression"
            listb = table_one_func(x, result)
            build_dict("Table", listb)
            # Hier Boxplot
            pie = df3.plot.box(figsize=(8, 8))
            fig = pie.get_figure()
            save_here = PATH_OUT + x + ".png"
            fig.savefig(save_here)
            build_dict("Image", x + ".png")
            fig.clf()
            print("in linear")
            max()
            print(df2)
    if korrelation and reg_one and reg_two:

        print("wir sind in korrelation")
        print(korrelation)
        df = df[[reg_one, reg_two]]
        df.dropna(how="any", inplace=True)

        var1 = df[reg_one]
        if reg_one in decimals:
            var1 = pandas.to_numeric(var1, errors='coerce')
        print(var1)
        var2 = df[reg_two]
        if reg_two in decimals:
            var2 = pandas.to_numeric(var2, errors='coerce')
        print(var2)
        result = scipy.stats.stats.pearsonr(var1, var2)
        x = reg_one + " und " + reg_two
        x = x.replace("_", "-")
        lista = ([x, " :Korrelation nach Pearson"], ["Korrelationskoeffizent", result[0]], ["P-Wert", result[1]])
        build_dict("Table", lista)
        print("in korrelation")
        max()

    if ttest_unv  and reg_one and reg_two:
        group1 = df[reg_one]
        group1 = group1.dropna()
        print(group1)
        group2 = df[reg_two]
        group2=group2.dropna()

        side = modus(mode_unv)
        print(side)

        result = scipy.stats.ttest_ind(group1, group2, alternative=side)
      
        if result[1] <= 0.05:
            emp = H0_x
        else:
            emp = H0_y
        
        x = reg_one + " and " + reg_two
        x = x.replace("_", "-")
        stat = str(result[0])
        p = str(result[1])

        lista = ([x, "TTest  unverbunden"], ["Stat", stat],["Seite",mode_unv], ["P-Value", p],["Empfehlung:",emp])
        build_dict("Table", lista)
        print("in ttest unv")
        max()


    if ttest_v  and reg_one and reg_two:
  
 
        group1 = df[reg_one]
        group1 = group1.dropna()
        print(group1)
        group2 = df[reg_two]
        group2=group2.dropna()
        

        k = len(group1)
 
        # using pop()
        # to truncate list
        n = len(group2)
        for i in range(0, n - k ):
            group2.pop(i)
        side = modus(mode_v)
        # printing result
        result = scipy.stats.ttest_rel(group1, group2, alternative=side)
        print(result)

        if result[1] <= 0.05:
            emp = H0_x
        else:
            emp = H0_y
        
        x = reg_one + " and " + reg_two
        x = x.replace("_", "-")
        stat = str(result[0])
        p = str(result[1])
        paar = len(group1)

        lista = ([x, "T-Test Verbunden"], ["Stat", stat], ["P-Value", p],["Seite",mode_v],["Wertepaare",paar],["Empfehlung: ",emp])
        lista = lista.replace("_", "-")
        build_dict("Table", lista)
        print("in ttest v")
        max()

    if utest  and reg_one and reg_two:

        print("u_test")
        group1 = df[reg_one]
        group1 = group1.dropna()
        print(group1)
        group2 = df[reg_two]
        group2=group2.dropna()
        
        side = modus(mode_u)

        result = scipy.stats.mannwhitneyu(group1,group2, alternative = side)
        print(result)
        if result[1] <= 0.05:
            emp = H0_x
        else:
            emp = H0_y
        
        x = reg_one + " and " + reg_two
        x = x.replace("_", "-")
        stat = str(result[0])
        p = str(result[1])
        paar = len(group1)

        lista = ([x, "U Test"], ["Stat", stat], ["P-Value", p],["Seite",mode_u],["Werte",paar],["Empfehlung: ",emp])
        lista = lista.replace("_", "-")
        build_dict("Table", lista)
        print("in utest")
        max()
    
    if will  and reg_one and reg_two:
 

        print("will")
        group1 = df[reg_one]
        group1 = group1.dropna()
        print(group1)
        group2 = df[reg_two]
        group2=group2.dropna()
        

        k = len(group1)
 
        # using pop()
        # to truncate list
        
        n = len(group2)
        for i in range(0, n - k ):
            group2.pop(i)
        side = modus(mode_w)
        result = scipy.stats.wilcoxon(group1, group2, alternative = side)
        if result[1] <= 0.05:
            emp = H0_x
        else:
            emp = H0_y
        
        x = reg_one + " and " + reg_two
        x = x.replace("_", "-")
        stat = str(result[0])
        p = str(result[1])
        paar = len(group1)

        lista = ([x, "Wilcoxon Rank Test"], ["Stat", stat], ["P-Value", p],["Seite",mode_w],["Wertepaare",paar],["Empfehlung: ",emp])
        lista = lista.replace("_", "-")
        build_dict("Table", lista)
        print("in will")
        max()

    if 1 == 0:
        print("logistische Regression")

        # Now we check the first variable and then set it
        global constans
        constans = []
        global bool_values
        bool_values = []
        check_variable(reg_one)
        check_variable(reg_two)
        try:
            x = sm.add_constant(constans)
            model = sm.Logit(bool_values, constans)
            result = model.fit(method='newton')
            print("hier results:")
            print(result)
        except Exception as e:
            print("hier fehler von log")
            print(e)
    print("wuhu, explorativ")

    print("help")

def reset_bar():
    global current_task 
    current_task = -1
    global status
    status = 0
    global max_task
    max_task = 1
    max()
##Hier wir nach dem Start für alle werte einmal statistik betrieben
def generate_pdf():
    
    tuple_list = [tuple(flask.session["elements"][i:i + 2]) for i in range(0, len(flask.session["elements"]), 2)]
    # Dokument schreiben
    currentdate = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    dokument = template.render(date_generated=currentdate, tuple_list=tuple_list)
    name = PATH_OUT + "Statistik-" + flask.session["username"]
    with codecs.open(name + ".tex", "w", "utf-8") as outputTex:
        outputTex.write(dokument)
        outputTex.close()
    print(tuple_list)

    # PDF rendern mit tectonic (https://tectonic-typesetting.github.io/), muss installiert und im PATH sein

    os.system("./tectonic -X compile " + name + ".tex")
    tuple_list = []
    for x in flask.session["elements"]:
        print(x)
        if (x["type"] == "Image"):
             os.remove(PATH_OUT + x["data"])
    os.remove(name + ".tex")
    reset_bar()
    return (name + ".pdf")
