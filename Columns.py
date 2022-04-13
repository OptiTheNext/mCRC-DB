d = ["SAPID",
  "Geschlecht",
  "Geburtsdatum",
  "LastChanged"
]

sql = "INSERT INTO KRK_Tabelle (SAPID, Geschlecht, Geburtsdatum, LastChanged) VALUES (%s, %s,%s,%s)"

sql_update = "UPDATE KRK_Tabelle SET SAPID  = %s, Geschlecht = %s, Geburtsdatum = %s, LastChanged = %s WHERE SAPID = %s"