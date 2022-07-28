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
