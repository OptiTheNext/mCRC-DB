# Bei der Änderung von Spalten in der Datenbank in d & b einfügen!!!!!!1!!!!1!!!!!!!!!!!!!!11!111!11!!!!!!!!!!!!!!11!!!!!!!1!!!!!!!!!!1!!!!!!1!!!!!

d = ["Kuerzel",
     "pat_id",
     "diagnosis1",
     "diagnosis2",
     "dob",
     "op_date_Surgery1",
     "op_date_Surgery2",
     "op_date_Surgery3",
     "op_code_Surgery1",
     "op_code_Surgery2",
     "op_code_Surgery3",
     "op_diagnosis_Surgery1",
     "op_diagnosis_Surgery2",
     "op_diagnosis_Surgery3",
     "pve_date",
     "pve",
     "study_id",
     "case_id",
     "age",
     "sex",
     "diagnosis_date",
     "primary_location",
     "T",
     "N",
     "LK",
     "M",
     "G",
     "L",
     "Pn",
     "V",
     "R",
     "RAS",
     "BRAF",
     "MSS",
     "crlm_met_syn",
     "crlm_procedure_planned",
     "crlm_procedure_realize",
     "crlm_bilobular",
     "multimodal",
     "two_staged",
     "date_fu",
     "status_fu",
     "recurrence_date",
     "recurrence_status",
     "recurrence_organ",
     "asa",
     "bmi",
     "alcohol",
     "smoking",
     "diabetes",
     "limax_initial",
     "limax_initial_date",
     "limax_second",
     "limax_second_date",
     "limax_third",
     "limax_third_date",
     "cirrhosis",
     "fibrosis",
     "previous_surgery",
     "previous_surgery_which",
     "previous_surgery_date",
     "fs_previous_chemotherapy",
     "fs_previous_chemotherapy_cycles",
     "fs_previous_chemotherapy_type",
     "fs_previous_antibody",
     "first_surgery_type",
     "first_surgery_minimal_invasive",
     "first_surgery_conversion",
     "first_surgery_ablation",
     "first_surgery_length",
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
     "fs_icu",
     "fs_los",
     "fs_dindo",
     "fs_complication_which",
     "second_surgery_planned",
     "second_surgery_realized",
     "ss_previous_chemotherapy",
     "ss_previous_chemotherapy_cycles",
     "ss_previous_chemotherapy_type",
     "ss_previous_antibody",
     "second_surgery_type",
     "second_surgery_minimal_invasive",
     "second_surgery_conversion",
     "second_surgery_ablation",
     "second_surgery_length",
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
     "ss_icu",
     "ss_los",
     "ss_dindo",
     "ss_complication_which",
     "third_surgery_planned",
     "third_surgery_realized",
     "th_previous_chemotherapy",
     "th_previous_chemotherapy_cycles",
     "th_previous_chemotherapy_type",
     "th_previous_antibody",
     "third_surgery_type",
     "third_surgery_minimal_invasiv",
     "third_surgery_conversion",
     "third_surgery_ablation",
     "third_surgery_length",
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
     "ts_AST_LAST",
     "ts_ALT_POD1",
     "ts_ALT_POD3",
     "ts_ALT_POD5",
     "ts_ALT_Last",
     "ts_INR_POD1",
     "ts_INR_POD3",
     "ts_INR_POD5",
     "ts_INR_Last",
     "ts_icu",
     "th_los",
     "ts_dindo",
     "ts_complication_which",
     "surgeries",
     "datediff_op1_op2",
     "pve_year",
     "op1year",
     "Kommentar"
     ]
b = ["Kuerzel",
     "PatientenID",
     "1. Diagnose",
     "2. Diagnose",
     "Geburtsdatum",
     "1. Op Datum",
     "2. Op Datum",
     "3. Op Datum",
     "1. Op Code",
     "2. Op Code",
     "3. Op Code",
     "1. Op Diagnose",
     "2. Op Diagnose",
     "3. Op Diagnose",
     "PVE Datum",
     "PVE",
     "Study ID",
     "Case ID",
     "Alter",
     "Geschlecht",
     "Diagnosedatum",
     "Primärlokalisation",
     "T",
     "N",
     "LK",
     "M",
     "G",
     "L",
     "Pn",
     "V",
     "R",
     "RAS",
     "BRAF",
     "MSS",
     "Synchron/Metachron",
     "Prozedur geplant?",
     "Prozedur umgesetzt?",
     "Bilobulär",
     "Multimodal",
     "Two Staged",
     "Zu letzt behandelt",
     "Verstorben",
     "Datum rezidiv",
     "Rezidivstatus",
     "Rezidivorgan",
     "ASA",
     "BMI",
     "Alkohol",
     "Rauchen",
     "Diabetes",
     "Limax initial",
     "Datum Limax inital",
     "zweiter Limax",
     "Datum zweiter Limax",
     "dritter Limax",
     "Datum dritter Limax",
     "Zirrose",
     "Fibrose",
     "Vorhergegangene OPs",
     "Vorhergegangene OP Type",
     "Datum Vorhergegangene OP",
     "Erste OP Chemo",
     "Erste OP Chemo Zyklen",
     "Erste OP Chemo Art",
     "Erste OP Antikörper",
     "Erste OP Typ",
     "Erste OP Minimal Invasiv",
     "Erste OP Konversion",
     "Erste OP Ablation",
     "Erste OP Länge",
     "Erste OP Serum Bili POD1",
     "Erste OP Serum Bili POD3",
     "Erste OP Serum Bili POD5",
     "Erste OP Serum Bili Last",
     "Erste OP Drainage Bili POD1",
     "Erste OP Drainage Bili POD3",
     "Erste OP Drainage Bili POD5",
     "Erste OP Drainage Bili Last",
     "Erste OP AST POD1",
     "Erste OP AST POD3",
     "Erste OP AST POD5",
     "Erste OP AST Last",
     "Erste OP ALT POD1",
     "Erste OP ALT POD3",
     "Erste OP ALT POD5",
     "Erste OP ALT Last",
     "Erste OP INR POD1",
     "Erste OP INR POD3",
     "Erste OP INR POD5",
     "Erste OP INR Last",
     "Erste OP Intensivzeit",
     "Erste OP Aufenthaltsdauer",
     "Erste OP DINDO",
     "Erste OP Komplikation",
     "Zweite OP Geplannt",
     "Zweite OP Umgesetzt",
     "Zweite OP vorherige Chemotherapien",
     "Zweite OP Chemo Zyklen",
     "Zweite OP Chemotyp",
     "Zweite OP vorherige Antikörper",
     "Zweite OP Typ",
     "Zweite OP Minimal Invasiv",
     "Zweite OP Konversion",
     "Zweite OP Ablation",
     "Zweite OP Länge",
     "Zweite OP Serum Bili POD1",
     "Zweite OP Serum Bili POD3",
     "Zweite OP Serum Bili POD5",
     "Zweite OP Serum Bili Last",
     "Zweite OP Drainage Bili POD1",
     "Zweite OP Drainage Bili POD3",
     "Zweite OP Drainage Bili POD5",
     "Zweite OP Drainage Bili Last",
     "Zweite OP AST POD1",
     "Zweite OP AST POD3",
     "Zweite OP AST POD5",
     "Zweite OP AST Last",
     "Zweite OP ALT POD1",
     "Zweite OP ALT POD3",
     "Zweite OP ALT POD5",
     "Zweite OP ALT Last",
     "Zweite OP INR POD1",
     "Zweite OP INR POD3",
     "Zweite OP INR POD5",
     "Zweite OP INR Last",
     "Zweite OP Intensivzeit",
     "Zweite OP Aufenthaltsdauer",
     "Zweite OP DINDO",
     "Zweite OP Komplikation",
     "Dritte OP geplant",
     "Dritte OP umgesetzt",
     "Dritte OP vorhergegangene Chemotherapie",
     "Dritte OP Chemo Zyklen",
     "Dritte OP Chemotherapie Typ",
     "Dritte OP Antikörper",
     "Dritte OP Typ",
     "Dritte OP Minimal Inversiv",
     "Dritte OP Konversion",
     "Dritte OP Ablation",
     "Dritte OP Länge",
     "Dritte OP Serum Bili POD1",
     "Dritte OP Serum Bili POD3",
     "Dritte OP Serum Bili POD5",
     "Dritte OP Serum Bili Last",
     "Dritte OP Drainage Bili POD1",
     "Dritte OP Drainage Bili POD3",
     "Dritte OP Drainage Bili POD5",
     "Dritte OP Drainage Bili Last",
     "Dritte OP AST POD1",
     "Dritte OP AST POD3",
     "Dritte OP AST POD5",
     "Dritte OP AST Last",
     "Dritte OP ALT POD1",
     "Dritte OP ALT POD3",
     "Dritte OP ALT POD5",
     "Dritte OP ALT Last",
     "Dritte OP INR POD1",
     "Dritte OP INR POD3",
     "Dritte OP INR POD5",
     "Dritte OP INR Last",
     "Dritte OP Intensivdauer",
     "Dritte OP Aufenthaltsdauer",
     "Dritte OP DINDO",
     "Dritte OP Komplikation",
     "Anzahl OPs",
     "Datumsdifferenz OP1 - OP2",
     "PVE Jahr",
     "Jahr der Ersten OP",
     "Kommentar"]

sql = "REPLACE INTO mcrc_tabelle ({}) VALUES "  # ON DUPLICATE KEY UPDATE"

sql_update = "UPDATE mcrc_tabelle SET SAPID  = %s, Geschlecht = %s, Geburtsdatum = %s, LastChanged = %s WHERE SAPID = %s"
