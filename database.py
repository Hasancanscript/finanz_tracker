import sqlite3
import matplotlib.pyplot as plt
import csv
import datetime
import locale
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from textwrap import wrap
from reportlab.lib.colors import red, green, black

# Verbindung zur Datenbank erstellen
conn = sqlite3.connect("finanz_tracker.db")
cursor = conn.cursor()

# Tabelle für Transaktionen erstellen (falls nicht vorhanden)
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()
conn.close()

# Funktion zum Hinzufügen einer Transaktion
def add_transaction(transaction_type, amount, category):
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO transactions (type, amount, category) VALUES (?, ?, ?)", 
                   (transaction_type, amount, category))
    
    conn.commit()
    conn.close()
    print(f"✅ Transaktion gespeichert: {category} - {amount:.2f} CHF")

# Funktion zum Anzeigen aller Transaktionen in sauberem Format
def show_transactions():
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    
    conn.close()

    if not rows:
        print("❌ Keine Transaktionen gefunden.")
        return
    
    print("\n📋 Alle Transaktionen:")
    print("=" * 80)
    print(f"{'ID':<5} {'Typ':<10} {'Betrag':<12} {'Kategorie':<20} {'Datum':<20}")
    print("=" * 80)
    
    for row in rows:
        print(f"{row[0]:<5} {row[1]:<10} {row[2]:<10.2f} CHF  {row[3]:<20} {row[4]:<20}")

    print("=" * 80)

# Funktion zum Berechnen der Gesamteinnahmen
def get_total_income():
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'Einnahme'")
    total_income = cursor.fetchone()[0] or 0
    
    conn.close()
    return total_income

# Funktion zum Berechnen der Gesamtausgaben
def get_total_expenses():
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'Ausgabe'")
    total_expenses = cursor.fetchone()[0] or 0
    
    conn.close()
    return total_expenses

# Funktion zum Berechnen des aktuellen Saldos
def get_balance():
    return get_total_income() - get_total_expenses()

# Funktion zur Erstellung eines Diagramms für Ausgaben nach Kategorie
def plot_expenses_by_category():
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT category, SUM(amount) FROM transactions WHERE type = 'Ausgabe' GROUP BY category")
    data = cursor.fetchall()
    
    conn.close()

    if not data:
        print("❌ Keine Ausgaben vorhanden, um ein Diagramm zu erstellen.")
        return

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    plt.figure(figsize=(8, 5))
    plt.bar(categories, amounts, color="red")
    plt.xlabel("Kategorie")
    plt.ylabel("Betrag in CHF")
    plt.title("Ausgaben nach Kategorie")
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    print("📊 Das Diagramm wird angezeigt...")
    plt.show()

# Funktion zum Exportieren der Transaktionen als CSV mit Datum
def export_to_csv():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"finanz_tracker_{today}.csv"

    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    
    conn.close()

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Typ", "Betrag", "Kategorie", "Datum"])
        writer.writerows(rows)

    print(f"✅ Daten erfolgreich als CSV gespeichert: {filename}")

# Funktion zum Exportieren der Transaktionen als PDF mit korrekter CHF-Ausrichtung
# Funktion zum Exportieren der Transaktionen als PDF/ Schweizer Zahlenformat setzen
locale.setlocale(locale.LC_NUMERIC, "de_CH.UTF-8")

def format_chf(amount):
    """Formatiert den Betrag als CHF mit Schweizer Trennzeichen (1'500.00)."""
    return f"CHF {locale.format_string('%.2f', amount, grouping=True)}"

def export_to_pdf():
    print("\n📄 PDF-Export-Optionen:")
    print("1️⃣ Alle Transaktionen exportieren")
    print("2️⃣ Nur einen bestimmten Monat exportieren")
    
    choice = input("Wähle eine Option (1 oder 2): ").strip()
    
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()

    if choice == "1":
        filename = f"finanz_tracker_{datetime.datetime.now().strftime('%Y-%m-%d')}.pdf"
        cursor.execute("SELECT * FROM transactions WHERE type = 'Einnahme'")
        einnahmen = cursor.fetchall()
        cursor.execute("SELECT * FROM transactions WHERE type = 'Ausgabe'")
        ausgaben = cursor.fetchall()
    elif choice == "2":
        year = input("Gib das Jahr ein (z. B. 2025): ").strip()
        month = input("Gib den Monat ein (1-12): ").strip().zfill(2)
        filename = f"finanz_tracker_{year}-{month}.pdf"

        cursor.execute("SELECT * FROM transactions WHERE type = 'Einnahme' AND strftime('%Y', date) = ? AND strftime('%m', date) = ?", (year, month))
        einnahmen = cursor.fetchall()
        
        cursor.execute("SELECT * FROM transactions WHERE type = 'Ausgabe' AND strftime('%Y', date) = ? AND strftime('%m', date) = ?", (year, month))
        ausgaben = cursor.fetchall()
    else:
        print("❌ Ungültige Eingabe. Abbruch.")
        return

    # Gesamtsummen berechnen
    total_income = sum(row[2] for row in einnahmen) if einnahmen else 0
    total_expenses = sum(row[2] for row in ausgaben) if ausgaben else 0
    balance = total_income - total_expenses

    conn.close()

    if not einnahmen and not ausgaben:
        print("❌ Keine passenden Transaktionen gefunden.")
        return

    # PDF-Erstellung
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(200, 750, "📊 Finanz-Tracker - Transaktionen")
    y = 720

    def draw_table_header(y_position, title, color):
        """Erstellt eine Tabellenüberschrift für Einnahmen und Ausgaben mit mehr Abstand."""
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(color)
        c.drawString(40, y_position, f"■ {title}")
        c.setFillColor("black")
        y_position -= 15
        c.setFont("Helvetica-Bold", 9)
        c.drawString(40, y_position, "ID")
        c.drawString(80, y_position, "Typ")
        c.drawString(160, y_position, "Kategorie")
        c.drawString(300, y_position, "Betrag")  # **Betrag jetzt linksbündig**
        c.drawString(420, y_position, "Datum")
        y_position -= 15
        c.setFont("Helvetica", 9)
        return y_position

    # Einnahmen anzeigen (falls vorhanden)
    if einnahmen:
        y = draw_table_header(y, "Einnahmen", "green")
        for row in einnahmen:
            c.drawString(40, y, str(row[0]))  # ID
            c.drawString(80, y, row[1])  # Typ
            c.drawString(160, y, row[3])  # Kategorie
            c.drawString(300, y, "CHF")  # **CHF jetzt links von der Zahl**
            c.drawRightString(380, y, locale.format_string('%.2f', row[2], grouping=True))  # **Betrag rechtsbündig**
            c.drawString(420, y, row[4])  # Datum
            y -= 20

    # Ausgaben anzeigen (falls vorhanden)
    if ausgaben:
        y -= 15
        y = draw_table_header(y, "Ausgaben", "red")
        for row in ausgaben:
            c.drawString(40, y, str(row[0]))  # ID
            c.drawString(80, y, row[1])  # Typ
            c.drawString(160, y, row[3])  # Kategorie
            c.drawString(300, y, "CHF")  # **CHF jetzt links von der Zahl**
            c.drawRightString(380, y, locale.format_string('%.2f', row[2], grouping=True))  # **Betrag rechtsbündig**
            c.drawString(420, y, row[4])  # Datum
            y -= 20

    # Gesamtsumme anzeigen
    y -= 20
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "■ Gesamteinnahmen:")
    c.drawString(300, y, "CHF")  # **CHF steht jetzt linksbündig**
    c.drawRightString(380, y, locale.format_string('%.2f', total_income, grouping=True))

    y -= 15
    c.drawString(40, y, "■ Gesamtausgaben:")
    c.drawString(300, y, "CHF")  # **CHF steht jetzt linksbündig**
    c.drawRightString(380, y, locale.format_string('%.2f', total_expenses, grouping=True))

    y -= 15
    c.setFillColor("green")
    c.drawString(40, y, "■ Verbleibendes Guthaben:")
    c.drawString(300, y, "CHF")  # **CHF steht jetzt linksbündig**
    c.drawRightString(380, y, locale.format_string('%.2f', balance, grouping=True))
    c.setFillColor("black")

    c.save()
    print(f"✅ PDF gespeichert: {filename}")

# Funktion zum Filtern der Transaktionen nach Monat
def filter_transactions_by_month(year, month):
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM transactions WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?", 
                   (str(year), f"{int(month):02d}"))
    rows = cursor.fetchall()
    
    conn.close()
    
    if not rows:
        print(f"❌ Keine Transaktionen für {month}/{year} gefunden.")
        return

    print(f"\n📅 Transaktionen für {month}/{year}:")
    for row in rows:
        print(f"ID: {row[0]}, Typ: {row[1]}, Betrag: {row[2]:.2f} CHF, Kategorie: {row[3]}, Datum: {row[4]}")
