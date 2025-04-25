# Finanz Tracker

Ein persönliches Tool zur Verwaltung und Analyse deiner Einnahmen und Ausgaben. Unterstützt sowohl eine Kommandozeilen-Oberfläche (CLI) als auch eine grafische Desktop-App (GUI).
Die grafische Desktop-App (GUI) befindet sich noch in der Überarbeitung und weist aktuell noch Fehler auf.

## Übersicht

- **SQLite-Datenbank**: `finanz_tracker.db` speichert alle Transaktionen.  
- **Transaktions-Management**: Einnahmen & Ausgaben hinzufügen, anzeigen, filtern.  
- **Reporting**: Diagramme (Matplotlib) und Exporte (CSV & PDF).  
- **Interfaces**:
  - **CLI** (`main.py`) für schnelle Eingaben und Auswertungen im Terminal  
  - **GUI** (`gui_ctk.py`) mit CustomTkinter & FPDF für eine moderne Desktop-App

## Funktionen

- Transaktion anlegen (Typ, Betrag, Kategorie, Datum)  
- Auflistung aller Transaktionen oder gefiltert nach Monat/Jahr  
- Gesamtsummen: Einnahmen, Ausgaben, Saldo  
- Plot: Ausgaben & Einnahmen pro Kategorie  
- CSV-Export für Tabellenkalkulationen  
- PDF-Export (mit Unicode-Font-Option für Smart-Quotes & Sonderzeichen)  
- Mehrfachausgaben in einem Schritt (z. B. `Miete:1500, Strom:80`)  
- Reset-Skript (`reset_database.py`) zum Löschen aller Daten und Zurücksetzen der IDs  

## Voraussetzungen

- Python 3.8 oder höher  
- SQLite (bereits enthalten)  
- Python-Pakete:
  - `customtkinter`
  - `fpdf`
  - `reportlab`
  - `matplotlib`

> **Tipp:** Erstelle eine virtuelle Umgebung:
> ```bash
> python3 -m venv venv
> source venv/bin/activate   # Linux/macOS
> venv\Scripts\activate      # Windows
> ```

## Installation

```bash
git clone https://github.com/dein-user/finanz_tracker.git
cd finanz_tracker
pip install customtkinter fpdf reportlab matplotlib
```

(Optional: `pip freeze > requirements.txt`)

## Nutzung

### CLI

```bash
python main.py
```

Menü:
1. Einnahme hinzufügen  
2. Ausgabe hinzufügen  
3. Alle Transaktionen anzeigen  
4. Einnahmen, Ausgaben & Saldo  
5. Ausgaben-Diagramm  
6. CSV-/PDF-Export  
7. Nach Monat/Jahr filtern  
0. Beenden  

### GUI

```bash
python gui_ctk.py
```

- Intuitive Buttons für alle Aktionen  
- Diagrammansicht und Tabelle  

## Konfiguration

Standardwerte (kannst du anpassen):
- **Datenbank-Pfad**: `finanz_tracker.db`  
- **Locale**: `de_CH.UTF-8` für Schweizer Zahlenformat  

## Datenbank zurücksetzen

Alle Transaktionen löschen und ID-Zähler zurücksetzen:

```bash
python reset_database.py
```

## Mitwirken

1. Fork des Repos  
2. Neuen Branch anlegen (`feature/meine-idee`)  
3. Änderungen commiten  
4. Pull-Request öffnen  