# Datenbank zum Kolorektalem Karzinom

## benötigte Umgebungsvariablen:

| Umgebungsvariable     | Bedeutung                                                                                                            |
| --------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `KRK_DB_HOST`         | IP/Host des MySQL-Datenbankservers                                                                                   |
| `KRK_DB_USER`         | Datenbankserver-Benutzername                                                                                         |
| `KRK_DB_PASS`         | Datenbankserver-Password                                                                                             |
| `KRK_DB_DATABASE`     | Zu nutzende Datenbank                                                                                                |
| `KRK_APP_HOST`        | IP-Adresse, auf welcher die Applikation verfügbar sein soll                                                          |
| `KRK_APP_PORT`        | Port, auf welchem die Applikation lauscht (Ports unterhalb von 1024 unter Linux i.d.R. nur mit root-Rechten nutzbar) |
| `KRK_DB_MAIL_SERVER`  | Email Server, von welchem die Mails verschickt werden sollen                                                         |
| `KRK_DB_MAIL_USER`    | Nutzername, auf dem besagtem Mail-Server                                                                             |
| `KRK_DB_MAIL_SENDER`  | Email-Adresse, zugehörig dem Nutzername                                                                              |
| `KRK_DB_MAIL_PASSWORD`| Passwort zur Email-Adresse / Nutzername                                                                              |
| `KRK_DB_SENDER`       | Absenderadresse für Emails
---

SystemD service file:

**Vor der Installation**
- MariaDB installieren
- Pfad der main.py in `ExecStart`
- Pfad des Arbeitsverzeichnisses in `WorkingDirectory` auf Pfad der geklonten Repository ändern
- Werte von `User` und `Group` entsprechend anpassen
- [Tectonic (LaTeX "Compiler")](https://tectonic-typesetting.github.io/en-US/index.html) installieren mit `curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net |sh`


**Installation**
```
sudo cp -v mcrc-db.service /etc/systemd/system #copy service file
sudo systemctl enable mcrc-db.service          #enable service
sudo systemctl start mcrc-db.service           #start service
sudo systemctl status mcrc-db.service          #check if the service started
sudo journalctl -f -u mcrc-db.service          #inspect the logs
```
**Deinstallation**
```
sudo systemctl stop mcrc-db.service
sudo systemctl disable mcrc-db.service
sudo systemctl daemon-reload
```

**Cronjobs**
Hier einmal kurz aufgeschlüsselt, wie die Cronjobs für die Richtige Benutzung aufzusetzen sind.
```
*/10 * * * * /usr/bin/python3 /path/to/delete_currently_active.py && printf "$(date -u)\n" 2>&1 >> /path/to/cron.log
0 3 * * * /usr/bin/git -C /path/to/directory pull --rebase && /usr/bin/pip install -r path/to/requirements.txt && /usr/bin/systemctl mcrc-db.service>
10 3 * * * /usr/bin/python3 path/to/backup_table.py
```
