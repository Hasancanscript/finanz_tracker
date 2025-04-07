import sqlite3
import datetime
import locale
import customtkinter as ctk
from PIL import Image, ImageTk
from fpdf import FPDF  # Stelle sicher, dass fpdf installiert ist (pip install fpdf)

# ----------------------------
# Datenbank-Funktionen & Setup
# ----------------------------

# Schweizer Zahlenformat einstellen (z. B. 6'500.00)
locale.setlocale(locale.LC_NUMERIC, "de_CH.UTF-8")

def update_schema():
    """
    Prüft, ob die Spalte 'exported' existiert und fügt sie hinzu, falls sie fehlt.
    """
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
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

def init_db():
    """
    Erstellt die Tabelle 'transactions', falls sie nicht existiert, und führt das Schema-Update aus.
    """
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            exported INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
    update_schema()

def add_transaction(ttype, amount, category):
    """
    Fügt eine neue Transaktion in die Datenbank ein.
    Der Parameter 'exported' wird automatisch auf 0 gesetzt.
    """
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO transactions (type, amount, category) VALUES (?, ?, ?)",
                   (ttype, amount, category))
    conn.commit()
    conn.close()
    print(f"✅ Transaktion gespeichert: {category} - {amount:.2f} CHF")

def format_date_str(date_str):
    """
    Parst das Datum (Format: YYYY-MM-DD HH:MM:SS) und gibt es im Format dd.mm.yyyy zurück.
    """
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    return dt.strftime("%d.%m.%Y")

def reset_transactions():
    """
    Löscht alle Transaktionen und setzt den AUTOINCREMENT-Zähler zurück.
    """
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='transactions'")
    conn.commit()
    conn.close()
    print("✅ Alle gespeicherten Transaktionen wurden gelöscht und ID zurückgesetzt!")

# Datenbank initialisieren
init_db()

# ----------------------------
# GUI-Funktionen
# ----------------------------

def chf_format(amount):
    """
    Erzeugt einen 16 Zeichen breiten String:
      - "CHF " (4 Zeichen) ganz links
      - Der Betrag (z. B. "  480.00") rechtsbündig in den restlichen 12 Zeichen
    Beispiel: "CHF       480.00" oder "CHF     1'800.00"
    """
    numeric_part = locale.format_string("%.2f", amount, grouping=True)
    numeric_part_aligned = f"{numeric_part:>12}"
    return f"CHF {numeric_part_aligned}"

def add_tx():
    """
    Liest die Eingabefelder aus, validiert die Eingabe und fügt eine neue Transaktion hinzu.
    Anschließend wird die Anzeige in der Textbox automatisch aktualisiert.
    """
    ttype = entry_type.get().strip()
    amount_str = entry_amount.get().strip()
    cat = entry_category.get().strip()

    if not ttype or not amount_str or not cat:
        label_info.configure(text="❌ Bitte alle Felder ausfüllen!", text_color="red")
        return

    # Tausendertrennzeichen entfernen
    amount_str = amount_str.replace("'", "")
    try:
        amount = float(amount_str)
    except ValueError:
        label_info.configure(text="❌ Betrag muss eine Zahl sein!", text_color="red")
        return

    # Neue Transaktion in der Datenbank speichern
    add_transaction(ttype, amount, cat)
    formatted_amount = locale.format_string("%.2f", amount, grouping=True)
    label_info.configure(text=f"✅ Gespeichert: {cat} - {formatted_amount} CHF", text_color="green")

    # Eingabefelder leeren
    entry_type.delete(0, ctk.END)
    entry_amount.delete(0, ctk.END)
    entry_category.delete(0, ctk.END)

    # Anzeige aktualisieren
    show_all_transactions()

def show_all_transactions():
    """
    Zeigt alle Transaktionen (Einnahmen und Ausgaben) in der Textbox an.
    Das Datum wird mit format_date_str() formatiert.
    """
    text_box.delete("1.0", ctk.END)
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE type='Einnahme'")
    incomes = cursor.fetchall()
    cursor.execute("SELECT * FROM transactions WHERE type='Ausgabe'")
    outcomes = cursor.fetchall()
    conn.close()

    total_incomes = sum(row[2] for row in incomes) if incomes else 0
    total_outcomes = sum(row[2] for row in outcomes) if outcomes else 0
    final_balance = total_incomes - total_outcomes

    header_format = "{:<3} | {:<9} | {:<22} | {:<16} | {:<10}\n"
    data_format   = "{:<3} | {:<9} | {:<22} | {} | {:<10}\n"

    # Einnahmen anzeigen
    text_box.insert("end", "Einnahmen\n", "green_text")
    text_box.insert("end", header_format.format("ID", "Typ", "Kategorie", "Betrag", "Datum"))
    text_box.insert("end", "-" * 80 + "\n")
    if not incomes:
        text_box.insert("end", "Keine Einnahmen vorhanden.\n")
    else:
        for row in incomes:
            row_id, row_type, row_amount, row_cat, row_date = row
            date_str = format_date_str(row_date)
            full_amount = chf_format(row_amount)
            line = data_format.format(str(row_id), row_type, row_cat, full_amount, date_str)
            text_box.insert("end", line)

    # Ausgaben anzeigen
    text_box.insert("end", "\nAusgaben\n", "red_text")
    text_box.insert("end", header_format.format("ID", "Typ", "Kategorie", "Betrag", "Datum"))
    text_box.insert("end", "-" * 80 + "\n")
    if not outcomes:
        text_box.insert("end", "Keine Ausgaben vorhanden.\n")
    else:
        for row in outcomes:
            row_id, row_type, row_amount, row_cat, row_date = row
            date_str = format_date_str(row_date)
            full_amount = chf_format(row_amount)
            line = data_format.format(str(row_id), row_type, row_cat, full_amount, date_str)
            text_box.insert("end", line)

    # Gesamtsummen anzeigen
    text_box.insert("end", "\n")
    summary_format = "{:<28}{}\n"
    sum_incomes_str = chf_format(total_incomes)
    sum_outcomes_str = chf_format(total_outcomes)
    final_str = chf_format(final_balance)
    text_box.insert("end", summary_format.format("Gesamteinnahmen:", sum_incomes_str))
    text_box.insert("end", summary_format.format("Gesamtausgaben:", sum_outcomes_str))
    text_box.insert("end", summary_format.format("Verbleibendes Guthaben:", final_str), "green_text")

def export_pdf():
    """
    Exportiert alle Transaktionen aus der Datenbank in eine PDF-Datei.
    Ein dynamischer Dateiname (mit Zeitstempel) verhindert Namenskonflikte.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Finanz Tracker Export", ln=True, align='C')
    pdf.ln(10)
    
    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    conn.close()
    
    # Tabellenkopf in der PDF
    pdf.cell(10, 10, txt="ID", border=1)
    pdf.cell(30, 10, txt="Typ", border=1)
    pdf.cell(50, 10, txt="Kategorie", border=1)
    pdf.cell(30, 10, txt="Betrag", border=1)
    pdf.cell(30, 10, txt="Datum", border=1)
    pdf.ln()
    
    for row in rows:
        row_id, row_type, row_amount, row_cat, row_date = row
        date_str = format_date_str(row_date)
        full_amount = chf_format(row_amount)
        pdf.cell(10, 10, txt=str(row_id), border=1)
        pdf.cell(30, 10, txt=row_type, border=1)
        pdf.cell(50, 10, txt=row_cat, border=1)
        pdf.cell(30, 10, txt=full_amount, border=1)
        pdf.cell(30, 10, txt=date_str, border=1)
        pdf.ln()
    
    timestamp = datetime.datetime.now().strftime("%d.%m.%Y_%H-%M-%S")
    filename = f"finanz_tracker_export_{timestamp}.pdf"
    pdf.output(filename)
    label_info.configure(text=f"PDF Export erfolgreich: {filename}", text_color="green")

def delete_all_transactions():
    """
    Löscht alle Transaktionen und aktualisiert die Anzeige.
    """
    reset_transactions()
    label_info.configure(text="✅ Alle Transaktionen wurden gelöscht!", text_color="green")
    show_all_transactions()

def close_app():
    app.destroy()

# Hover-Effekte (optional)
def on_enter(event):
    event.widget.configure(fg_color="lightblue")

def on_leave(event):
    event.widget.configure(fg_color="dark-blue")

# ----------------------------
# GUI-Einstellungen & Layout
# ----------------------------
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("Finanz-Tracker (Dark Mode)")
app.geometry("800x650")
app.configure(fg_color="#2B2B2B")

# Logo (optional)
try:
    logo_img = Image.open("logo.png").resize((200, 200))
    logo_ctk = ImageTk.PhotoImage(logo_img)
    label_logo = ctk.CTkLabel(app, image=logo_ctk, text="")
    label_logo.pack(pady=(10, 0))
except Exception as e:
    print("Kein Logo gefunden oder Fehler beim Laden:", e)

# Titeltext
label_title = ctk.CTkLabel(app,
    text="Willkommen beim Finanz-Tracker!\nBehalte deine Finanzen im Blick und manage sie mühelos.",
    font=("Consolas", 20))
label_title.pack(pady=(0, 10))

# Frame für Eingaben
frame_inputs = ctk.CTkFrame(app, fg_color="#333333", width=400)
frame_inputs.pack(pady=10, padx=10)

label_type = ctk.CTkLabel(frame_inputs, text="Typ (Einnahme/Ausgabe):", font=("Consolas", 12))
label_type.grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_type = ctk.CTkEntry(frame_inputs, placeholder_text="z. B. Einnahme", width=300)
entry_type.grid(row=0, column=1, padx=5, pady=5)

label_amount = ctk.CTkLabel(frame_inputs, text="Betrag in CHF:", font=("Consolas", 12))
label_amount.grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_amount = ctk.CTkEntry(frame_inputs, placeholder_text="z. B. 6'500.00", width=300)
entry_amount.grid(row=1, column=1, padx=5, pady=5)

label_category = ctk.CTkLabel(frame_inputs, text="Kategorie:", font=("Consolas", 12))
label_category.grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry_category = ctk.CTkEntry(frame_inputs, placeholder_text="z. B. Lohn / Miete", width=300)
entry_category.grid(row=2, column=1, padx=5, pady=5)

btn_add = ctk.CTkButton(frame_inputs, text="Transaktion hinzufügen", command=add_tx)
btn_add.grid(row=3, column=0, columnspan=2, pady=10)

# Info-Label
label_info = ctk.CTkLabel(app, text="", text_color="green", font=("Consolas", 12))
label_info.pack()

# Button: Transaktionen anzeigen
btn_show = ctk.CTkButton(app, text="Transaktionen (PDF-Stil) anzeigen", command=show_all_transactions)
btn_show.pack(pady=10)

# Button: PDF Export
btn_export = ctk.CTkButton(app, text="Exportiere als PDF", command=export_pdf)
btn_export.pack(pady=10)
btn_export.bind("<Enter>", on_enter)
btn_export.bind("<Leave>", on_leave)

# Button: Alle Transaktionen löschen (Reset)
btn_delete = ctk.CTkButton(app, text="Alle Transaktionen löschen", command=delete_all_transactions)
btn_delete.pack(pady=10)
btn_delete.bind("<Enter>", on_enter)
btn_delete.bind("<Leave>", on_leave)

# Textbox zur Anzeige der Transaktionen
text_box = ctk.CTkTextbox(app, width=780, height=350)
text_box.configure(font=("Courier New", 12))
text_box.pack(pady=5)
text_box.tag_config("green_text", foreground="green")
text_box.tag_config("red_text", foreground="red")

# Button: Anwendung beenden
btn_close = ctk.CTkButton(app, text="Beenden", command=close_app)
btn_close.pack(pady=20)
btn_close.bind("<Enter>", on_enter)
btn_close.bind("<Leave>", on_leave)

app.mainloop()
