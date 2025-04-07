import sqlite3
import matplotlib.pyplot as plt
import csv
import datetime
import locale
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from textwrap import wrap
from reportlab.lib.colors import red, green, black

# ------------------------------
# Schema-Update: Spalte 'exported'
# ------------------------------
def update_schema():
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    # Prüfen, ob die Tabelle existiert und welche Spalten vorhanden sind
    cursor.execute("PRAGMA table_info(transactions)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'exported' not in columns:
        try:
            cursor.execute("ALTER TABLE transactions ADD COLUMN exported INTEGER DEFAULT 0")
            conn.commit()
            print("✅ Spalte 'exported' erfolgreich zur Tabelle hinzugefügt.")
        except Exception as e:
            print("❌ Fehler beim Hinzufügen der Spalte 'exported':", e)
    conn.close()

# ------------------------------
# Datenbank und Tabelle erstellen
# ------------------------------
conn = sqlite3.connect("finanz_tracker.db")
cursor = conn.cursor()
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

# Schema-Update ausführen (fügt 'exported' hinzu, falls noch nicht vorhanden)
update_schema()

# ------------------------------
# Funktionen zur Verwaltung der Transaktionen
# ------------------------------

def add_transaction(transaction_type, amount, category):
    """Speichert eine neue Transaktion in der Datenbank."""
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    # exported wird hier automatisch auf 0 gesetzt (Default)
    cursor.execute("INSERT INTO transactions (type, amount, category) VALUES (?, ?, ?)",
                   (transaction_type, amount, category))
    conn.commit()
    conn.close()
    print(f"✅ Transaktion gespeichert: {category} - {amount:.2f} CHF")

def show_transactions():
    """Zeigt alle Transaktionen formatiert in der Konsole an."""
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

def get_all_transactions():
    """Gibt eine Liste aller Transaktionen zurück (für z. B. Web/Flask)."""
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, type, amount, category, date FROM transactions")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_total_income():
    """Berechnet die Gesamteinnahmen."""
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'Einnahme'")
    total_income = cursor.fetchone()[0] or 0
    conn.close()
    return total_income

def get_total_expenses():
    """Berechnet die Gesamtausgaben."""
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'Ausgabe'")
    total_expenses = cursor.fetchone()[0] or 0
    conn.close()
    return total_expenses

def get_balance():
    """Berechnet den aktuellen Saldo (Einnahmen - Ausgaben)."""
    return get_total_income() - get_total_expenses()

# ------------------------------
# Diagramme (Matplotlib)
# ------------------------------

def plot_expenses_by_category():
    """Erstellt ein Balkendiagramm der Ausgaben nach Kategorie."""
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

def plot_incomes_and_expenses_by_category():
    """
    Erstellt ein Balkendiagramm, in dem pro Kategorie zwei Balken dargestellt werden:
    - Einnahmen (grün)
    - Ausgaben (rot)
    """
    import numpy as np
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, type, SUM(amount)
        FROM transactions
        GROUP BY category, type
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("❌ Keine Transaktionen vorhanden, um ein Diagramm zu erstellen.")
        return

    categories_data = {}
    for (category, ttype, amount) in rows:
        if category not in categories_data:
            categories_data[category] = {"Einnahme": 0, "Ausgabe": 0}
        categories_data[category][ttype] = amount

    categories = sorted(categories_data.keys())
    incomes = [categories_data[cat]["Einnahme"] for cat in categories]
    expenses = [categories_data[cat]["Ausgabe"] for cat in categories]

    if sum(incomes) == 0 and sum(expenses) == 0:
        print("❌ Weder Einnahmen noch Ausgaben vorhanden, um ein Diagramm zu erstellen.")
        return

    x = np.arange(len(categories))
    width = 0.4

    plt.figure(figsize=(10, 6))
    plt.bar(x - width/2, incomes, width, label="Einnahmen", color="green")
    plt.bar(x + width/2, expenses, width, label="Ausgaben", color="red")
    plt.xticks(x, categories, rotation=45)
    plt.xlabel("Kategorie", fontsize=12)
    plt.ylabel("Betrag in CHF", fontsize=12)
    plt.title("Einnahmen und Ausgaben pro Kategorie", fontsize=14, fontweight="bold")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    print("📊 Das Diagramm wird angezeigt...")
    plt.show()

# ------------------------------
# Export-Funktionen (CSV & PDF)
# ------------------------------

def export_to_csv():
    """Exportiert alle Transaktionen als CSV-Datei."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"finanz_tracker_{today}.csv"
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    conn.close()
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Typ", "Betrag", "Kategorie", "Datum", "Exported"])
        writer.writerows(rows)
    print(f"✅ Daten erfolgreich als CSV gespeichert: {filename}")

# Schweizer Zahlenformat setzen
locale.setlocale(locale.LC_NUMERIC, "de_CH.UTF-8")

def format_chf(amount):
    """Formatiert den Betrag als CHF mit Schweizer Trennzeichen (1'500.00)."""
    return f"CHF {locale.format_string('%.2f', amount, grouping=True)}"

def format_date_str(date_str):
    """Parst das Datenbank-Datum und formatiert es als dd.mm.yyyy."""
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%d.%m.%Y")

def export_to_pdf():
    """
    Exportiert die Transaktionen als PDF.
    Dabei werden nur Transaktionen mit exported = 0 berücksichtigt.
    Nach erfolgreichem Export werden diese Einträge als exportiert markiert.
    """
    print("\n📄 PDF-Export-Optionen:")
    print("1️⃣ Alle Transaktionen exportieren (nur noch nicht exportierte)")
    print("2️⃣ Nur einen bestimmten Monat exportieren (nicht exportierte)")
    choice = input("Wähle eine Option (1 oder 2): ").strip()
    
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()

    # Zeitstempel zur eindeutigen Dateinamenbildung (Datum und Uhrzeit)
    timestamp = datetime.datetime.now().strftime("%d.%m.%Y_%H-%M-%S")
    
    if choice == "1":
        filename = f"finanz_tracker_{timestamp}.pdf"
        cursor.execute("SELECT * FROM transactions WHERE type = 'Einnahme' AND exported = 0")
        einnahmen = cursor.fetchall()
        cursor.execute("SELECT * FROM transactions WHERE type = 'Ausgabe' AND exported = 0")
        ausgaben = cursor.fetchall()
    elif choice == "2":
        year = input("Gib das Jahr ein (z. B. 2025): ").strip()
        month = input("Gib den Monat ein (1-12): ").strip().zfill(2)
        filename = f"finanz_tracker_{month}.{year}_{timestamp}.pdf"
        cursor.execute("""
            SELECT * FROM transactions 
            WHERE type = 'Einnahme' AND exported = 0
              AND strftime('%Y', date) = ? 
              AND strftime('%m', date) = ?
        """, (year, month))
        einnahmen = cursor.fetchall()
        cursor.execute("""
            SELECT * FROM transactions 
            WHERE type = 'Ausgabe' AND exported = 0
              AND strftime('%Y', date) = ? 
              AND strftime('%m', date) = ?
        """, (year, month))
        ausgaben = cursor.fetchall()
    else:
        print("❌ Ungültige Eingabe. Abbruch.")
        conn.close()
        return

    total_income = sum(row[2] for row in einnahmen) if einnahmen else 0
    total_expenses = sum(row[2] for row in ausgaben) if ausgaben else 0
    balance = total_income - total_expenses

    if not einnahmen and not ausgaben:
        print("❌ Keine passenden Transaktionen gefunden.")
        conn.close()
        return

    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(200, 750, "📊 Finanz-Tracker - Transaktionen")
    y = 720

    def draw_table_header(y_position, title, color):
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(color)
        c.drawString(40, y_position, f"■ {title}")
        c.setFillColor("black")
        y_position -= 15
        c.setFont("Helvetica-Bold", 9)
        c.drawString(40, y_position, "ID")
        c.drawString(80, y_position, "Typ")
        c.drawString(160, y_position, "Kategorie")
        c.drawString(300, y_position, "Betrag")
        c.drawString(420, y_position, "Datum")
        y_position -= 15
        c.setFont("Helvetica", 9)
        return y_position

    if einnahmen:
        y = draw_table_header(y, "Einnahmen", green)
        for row in einnahmen:
            c.drawString(40, y, str(row[0]))
            c.drawString(80, y, row[1])
            c.drawString(160, y, row[3])
            c.drawString(300, y, "CHF")
            c.drawRightString(380, y, locale.format_string('%.2f', row[2], grouping=True))
            c.drawString(420, y, format_date_str(row[4]))
            y -= 20

    if ausgaben:
        y -= 15
        y = draw_table_header(y, "Ausgaben", red)
        for row in ausgaben:
            c.drawString(40, y, str(row[0]))
            c.drawString(80, y, row[1])
            c.drawString(160, y, row[3])
            c.drawString(300, y, "CHF")
            c.drawRightString(380, y, locale.format_string('%.2f', row[2], grouping=True))
            c.drawString(420, y, format_date_str(row[4]))
            y -= 20

    y -= 20
    c.setFont("Helvetica-Bold", 10)
    c.drawString(40, y, "■ Gesamteinnahmen:")
    c.drawString(300, y, "CHF")
    c.drawRightString(380, y, locale.format_string('%.2f', total_income, grouping=True))
    y -= 15
    c.drawString(40, y, "■ Gesamtausgaben:")
    c.drawString(300, y, "CHF")
    c.drawRightString(380, y, locale.format_string('%.2f', total_expenses, grouping=True))
    y -= 15
    c.setFillColor(green)
    c.drawString(40, y, "■ Verbleibendes Guthaben:")
    c.drawString(300, y, "CHF")
    c.drawRightString(380, y, locale.format_string('%.2f', balance, grouping=True))
    c.setFillColor("black")
    c.save()

    print(f"✅ PDF gespeichert: {filename}")

    if choice == "1":
        cursor.execute("UPDATE transactions SET exported = 1 WHERE type IN ('Einnahme', 'Ausgabe') AND exported = 0")
    elif choice == "2":
        cursor.execute("""
            UPDATE transactions 
            SET exported = 1 
            WHERE type IN ('Einnahme', 'Ausgabe') 
              AND exported = 0 
              AND strftime('%Y', date) = ? 
              AND strftime('%m', date) = ?
        """, (year, month))
    conn.commit()
    conn.close()

# ------------------------------
# Filter- und Reset-Funktionen
# ------------------------------

def filter_transactions_by_month(year, month):
    """Filtert und zeigt Transaktionen für einen bestimmten Monat in der Konsole an."""
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

def reset_transactions():
    """Löscht alle Transaktionen und setzt den ID-Zähler zurück."""
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='transactions'")
    conn.commit()
    conn.close()
    print("✅ Alle gespeicherten Transaktionen wurden gelöscht und ID zurückgesetzt!")