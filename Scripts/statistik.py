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
    # Laborwerte
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
    # Zweite OP
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
    # Dritte OP
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
    # Zweite OP
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
    # Dritte OP
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
            continue

        current_name = x
        current_df = df[x]
        current_df.dropna(inplace=True)

        #Format input df for better functionality with statistical libaries
        if x in booleans:
            df = df.replace({0: False, 1: True})

        if x in decimals:
            current_df = pandas.to_numeric(current_df, errors='coerce')

        if x in categorials:
            current_df = current_df.astype(str)
            current_df[1] = current_df.replace("", numpy.nan, inplace=True)
            current_df[1] = current_df.dropna(inplace=True)
        #Generate table one if wanted
        if (table_one):
            result = current_df.describe()
            table = table_one_func(x, result)  # table is ne liste
            build_dict("Table", table)
        #Generate A Graph from Table One
        if (grafik):
            #Generate Graph as Cake Graph
            if x in booleans:
                values = current_df.value_counts()
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
            if x in categorials:
                current_df = current_df.value_counts()
                pie = current_df.plot.bar(figsize=(6, 6))
                fig = pie.get_figure()
                save_here = PATH_OUT + flask.session["username"] + "_" + x + "_balken.png"
                fig.savefig(save_here)
                build_dict("Image", flask.session["username"] + "_" + x + "_balken.png")
                fig.clf()


def normalverteilung(df, points_of_interest, saphiro, kolmogorov, anderson, qqplot, histo):
    # Test auf Normalverteilung und entsprechender T-Test
    for x in points_of_interest:
        if x in decimals:
            # Vorbereitungen: Spalte rausziehen, zu numbern, leere spalten loswerden
            df = pandas.DataFrame(df)
            df = df[x]

            df = pandas.to_numeric(df, errors='coerce')

            df = df[~numpy.isnan(df)]

            if (saphiro == True):
                result = scipy.stats.shapiro(df)
                table = ([x, " :Saphiro-Wilkoson Test"], ["Teststatistik", result[0]], ["P-Wert", result[1]])
                build_dict("Table", table)
            if (kolmogorov == True):
                result = scipy.stats.kstest(df, 'norm')
                table = ([x, " :Kolmogorov-Smirnov Test"], ["Teststatistik", result[0]], ["P-Wert", result[1]])
                build_dict("Table", table)
            if (anderson == True):
                result = scipy.stats.anderson(df)
                table = ([x, " :Anderson-Test"], ["Teststatistik", result[0]], ["Kritische Werte", result[1]],
                         ["Signifikanslevel", result[2]])
                build_dict("Table", table)
            if (qqplot == True):
                fig = sm.qqplot(df, line='45', xlabel='Zu erwartende Werte', ylabel=x, figsize=(6, 6))
                save_here = PATH_OUT + x + ".png"
                fig.savefig(save_here)
                build_dict("Image", x + "_qqplot.png")
                fig.clf()
            if (histo == True):
                print("hier histo")
                fig, ax = matplotlib.pyplot.subplots()
                df.plot.kde(ax=ax, legend=False)
                df.plot.hist(density=True, ax=ax, figsize=(6, 6))
                ax.set_ylabel('Probability')
                ax.grid(axis='y')
                ax.set_facecolor('#d8dcd6')
                save_here = PATH_OUT + flask.session["username"] + "_" + x + "_histo.png"
                fig.savefig(save_here)
                build_dict("Image", flask.session["username"] + "_" + x + "_histo.png")
                fig.clf()

    print("Wuhu, normalverteilt")


def exploration(df, points_of_interest, reg_one, reg_two, linear, korrelation, ttest_v, ttest_unv, utest, will, mode_unv, mode_v, mode_u,mode_w):
    # Test / Darstellung von korrellation
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

        slope, intercept, r, p, se = scipy.stats.linregress(xwerte, y=ywerte, alternative='two-sided')
        return slope

    if linear:
        for x in point_of_interest:
            if verlauf_check(x):
                continue
            # now we need to create a new dataframe with all of the Data in linearer regression zum vergleich
            value = op_nm + "_"
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

            listb = table_one_func(x, result)
            build_dict("Table", listb)
            # Hier Boxplot
            pie = df3.plot.box(figsize=(8, 8))
            fig = pie.get_figure()
            save_here = PATH_OUT + x + ".png"
            fig.savefig(save_here)
            build_dict("Image", x + ".png")
            fig.clf()

            print(df2)
    if korrelation:
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
        lista = ([x, " :Korrelation nach Pearson"], ["Korrelationskoeffizent", result[0]], ["P-Wert", result[1]])
        build_dict("Table", lista)

    if ttest_unv:
        group1 = df[reg_one]
        group1 = group1.dropna()
        print(group1)
        group2 = df[reg_two]
        group2=group2.dropna()

        side = modus(mode_unv)
        print(side)

        result = scipy.stats.ttest_ind(group1, group2, alternative=side)
      
        if result[1] <= 0.05:
            emp = "H0 verwerfen"
        else:
            emp = "H0 annehmen"
        
        x = reg_one + " and " + reg_two
        x = x.replace("_", "-")
        stat = str(result[0])
        p = str(result[1])

        lista = ([x, "TTest  unverbunden"], ["Stat", stat],["Seite",mode_unv], ["P-Value", p],["Empfehlung: ",emp])
        build_dict("Table", lista)

    if ttest_v:
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
            emp = "H0 verwerfen"
        else:
            emp = "H0 annehmen"
        
        x = reg_one + " and " + reg_two
        x = x.replace("_", "-")
        stat = str(result[0])
        p = str(result[1])
        paar = len(group1)

        lista = ([x, "T-Test Verbunden"], ["Stat", stat], ["P-Value", p],["Seite",mode_v],["Wertepaare",paar],["Empfehlung: ",emp])
        build_dict("Table", lista)

    if utest:
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
            emp = "H0 verwerfen"
        else:
            emp = "H0 annehmen"
        
        x = reg_one + " and " + reg_two
        x = x.replace("_", "-")
        stat = str(result[0])
        p = str(result[1])
        paar = len(group1)

        lista = ([x, "U Test"], ["Stat", stat], ["P-Value", p],["Seite",mode_u],["Werte",paar],["Empfehlung: ",emp])
        build_dict("Table", lista)
    
    if will:
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
            emp = "H0 verwerfen"
        else:
            emp = "H0 annehmen"
        
        x = reg_one + " and " + reg_two
        x = x.replace("_", "-")
        stat = str(result[0])
        p = str(result[1])
        paar = len(group1)

        lista = ([x, "Wilcoxon Rank Test"], ["Stat", stat], ["P-Value", p],["Seite",mode_w],["Wertepaare",paar],["Empfehlung: ",emp])
        build_dict("Table", lista)

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
    #os.remove(name + ".tex")

    return (name + ".pdf")
