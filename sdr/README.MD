Files:
===
aquire-868.grc
===
GRC Code zum mitschneiden der Daten

minimalPlot.ipynb
===
Beispiel zur Auswertung der Daten

gather.py
===
von GRC generierter code, angepasst zur automatischen auswertung

Start
---
./gather.py [Name für Messung] [--tresh threshold für signal]

Ausgabe
---
sampleFile.complex32: Rohe Messdaten

sampleFile-res.txt: Ergebniss der Auswertung, Dict aus Start eines Signals: Länge des Signals
