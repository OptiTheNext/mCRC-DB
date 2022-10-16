# Datenbank zum Kolorektalem Karzinom

## benötigte Umgebungsvariablen:

| Umgebungsvariable | Bedeutung                                                                                                            |
| ----------------- | -------------------------------------------------------------------------------------------------------------------- |
| `KRK_DB_HOST`     | IP/Host des MySQL-Datenbankservers                                                                                   |
| `KRK_DB_USER`     | Datenbankserver-Benutzername                                                                                         |
| `KRK_DB_PASS`     | Datenbankserver-Password                                                                                             |
| `KRK_DB_DATABASE` | Zu nutzende Datenbank                                                                                                |
| `KRK_APP_HOST`    | IP-Adresse, auf welcher die Applikation verfügbar sein soll                                                          |
| `KRK_APP_PORT`    | Port, auf welchem die Applikation lauscht (Ports unterhalb von 1024 unter Linux i.d.R. nur mit root-Rechten nutzbar) |

---

SystemD service file:

**Vor der Installation**
Pfad der main.py in `ExecStart`
Pfad des Arbeitsverzeichnisses in `WorkingDirectory` auf Pfad der geklonten Repository ändern
Werte von `User` und `Group` entsprechend anpassen


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
  GNU nano 4.8                                                          /tmp/crontab.wvZw7H/crontab                                                           Modified  # Edit this file to introduce tasks to be run by cron.
#
# Each task to run has to be defined through a single line
# indicating with different fields when the task will be run
# and what command to run for the task
#
# To define the time you can provide concrete values for
# minute (m), hour (h), day of month (dom), month (mon),
# and day of week (dow) or use '*' in these fields (for 'any').
#
# Notice that tasks will be started based on the cron's system
# daemon's notion of time and timezones.
#
# Output of the crontab jobs (including errors) is sent through
# email to the user the crontab file belongs to (unless redirected).

*/10 * * * * /usr/bin/python3 /path/to/delete_currently_active.py && printf "$(date -u)\n" 2>&1 >> /path/to/cron.log
0 3 * * * /usr/bin/git -C /path/to/directory pull --rebase && /usr/bin/pip install -r path/to/requirements.txt && /usr/bin/systemctl mcrc-db.service>
0 3 * * * /usr/bin/python3 path/to/backup_table.py
```
