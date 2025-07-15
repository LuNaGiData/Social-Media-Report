# 📊 Social Media Campaign Report

Ein interaktives Dashboard für kanalübergreifende Social Media Auswertungen – gebaut mit [Streamlit](https://streamlit.io/).

## ✨ Features

- Zeitfilter & Plattform-Filter im Browser
- KPI-Übersicht mit Benchmark-Vergleich
- Kuchendiagramm & Zeitverlauf
- Top/Flop-Beiträge je Plattform (farbiges Performance-Ranking)
- Alle Posts in einer Übersicht – Performance farbig!
- Responsive & sofort teilbar

## 🚀 Schnellstart

1. **Projekt herunterladen oder klonen**
   git clone https://github.com/DEINNAME/social-media-report.git
   cd magic-social-dashboard

2. **(Optional) Virtuelle Umgebung aktivieren**
   python3 -m venv venv
   source venv/bin/activate

3. **Abhängigkeiten installieren**
   pip install -r requirements.txt

4. **Dashboard starten**
   streamlit run app.py

5. **Im Browser anschauen**
   (Standard: http://localhost:8501)

## 🗃️ Datenstruktur

- **data_export.csv**: Social-Media-Export, z.B. aus Facebook, Instagram, TikTok, X, LinkedIn, YouTube  
  Enthält mindestens folgende Spalten:  
  Plattform, Titel, Impressionen, Interaktionen, Klicks, Videoaufrufe, Datum, ...

- **benchmarks.csv**:  
  Durchschnittswerte pro Plattform als Benchmark


## 👤 Copyright

© Luca Napolitano Gil  
Freigegeben unter MIT License

## 🤝 Kontakt & Feedback

Fragen? Verbesserungsvorschläge?  
luca@lunagi.eu
