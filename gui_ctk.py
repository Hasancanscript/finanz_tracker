import customtkinter as ctk
from PIL import Image, ImageTk
import sqlite3
import locale

# Aus deiner database.py importieren wir Funktionen:
from database import add_transaction, format_date_str

# Schweizer Betragsformat (z. B. 6'500.00)
locale.setlocale(locale.LC_NUMERIC, "de_CH.UTF-8")

def add_tx():
    """
    Fügt eine neue Transaktion hinzu (Einnahme oder Ausgabe).
    Betrag kann mit ' angegeben werden, z. B. 1'800.00
    """
    ttype = entry_type.get().strip()
    amount_str = entry_amount.get().strip()
    cat = entry_category.get().strip()

    if not ttype or not amount_str or not cat:
        label_info.configure(text="❌ Bitte alle Felder ausfüllen!", text_color="red")
        return

    # Entferne Tausendertrennzeichen (')
    amount_str = amount_str.replace("'", "")

    try:
        amount = float(amount_str)
    except ValueError:
        label_info.configure(text="❌ Betrag muss eine Zahl sein!", text_color="red")
        return

    add_transaction(ttype, amount, cat)

    # Formatierter Betrag für Rückmeldung
    formatted_amount = locale.format_string("%.2f", amount, grouping=True)
    label_info.configure(text=f"✅ Gespeichert: {cat} - {formatted_amount} CHF", text_color="green")

    # Eingabefelder leeren
    entry_type.delete(0, ctk.END)
    entry_amount.delete(0, ctk.END)
    entry_category.delete(0, ctk.END)

def show_all_transactions():
    """
    Zeigt Einnahmen und Ausgaben getrennt, wie im PDF.
    Spalten: ID, Typ, Kategorie, Betrag, Datum
    Am Ende: Gesamteinnahmen, Gesamtausgaben, Verbleibendes Guthaben
    """
    text_box.delete("1.0", ctk.END)

    conn = sqlite3.connect("finanz_tracker.db")
    cursor = conn.cursor()

    # Einnahmen
    cursor.execute("SELECT * FROM transactions WHERE type='Einnahme'")
    incomes = cursor.fetchall()

    # Ausgaben
    cursor.execute("SELECT * FROM transactions WHERE type='Ausgabe'")
    outcomes = cursor.fetchall()

    # Gesamtsummen berechnen
    total_incomes = sum(row[2] for row in incomes) if incomes else 0
    total_outcomes = sum(row[2] for row in outcomes) if outcomes else 0
    final_balance = total_incomes - total_outcomes

    conn.close()

    # ---------------------------
    # EINNAHMEN
    # ---------------------------
    text_box.insert("end", "Einnahmen\n")
    text_box.insert("end", "ID  | Typ       | Kategorie               | Betrag        | Datum     \n")
    text_box.insert("end", "-" * 80 + "\n")

    if not incomes:
        text_box.insert("end", "Keine Einnahmen vorhanden.\n")
    else:
        for row in incomes:
            row_id = row[0]
            row_type = row[1]
            row_amount = row[2]
            row_cat = row[3]
            row_date = row[4]

            date_str = format_date_str(row_date)  # dd.mm.yyyy
            amount_str = locale.format_string("%.2f", row_amount, grouping=True)

            # Spaltenbreiten:
            # ID: 3 (links), Typ: 9 (links), Kategorie: 22 (links),
            # Betrag: 12 (rechts) + " CHF", Datum: 10 (links)
            line = (f"{str(row_id):<3} | "
                    f"{row_type:<9} | "
                    f"{row_cat:<22} | "
                    f"{amount_str:>12} CHF | "
                    f"{date_str:<10}\n")
            text_box.insert("end", line)

    text_box.insert("end", "\nAusgaben\n")
    text_box.insert("end", "ID  | Typ       | Kategorie               | Betrag        | Datum     \n")
    text_box.insert("end", "-" * 80 + "\n")

    if not outcomes:
        text_box.insert("end", "Keine Ausgaben vorhanden.\n")
    else:
        for row in outcomes:
            row_id = row[0]
            row_type = row[1]
            row_amount = row[2]
            row_cat = row[3]
            row_date = row[4]

            date_str = format_date_str(row_date)
            amount_str = locale.format_string("%.2f", row_amount, grouping=True)

            line = (f"{str(row_id):<3} | "
                    f"{row_type:<9} | "
                    f"{row_cat:<22} | "
                    f"{amount_str:>12} CHF | "
                    f"{date_str:<10}\n")
            text_box.insert("end", line)

    # ---------------------------
    # Gesamtsummen (wie im PDF)
    # ---------------------------
    text_box.insert("end", "\n")
    sum_incomes_str = locale.format_string("%.2f", total_incomes, grouping=True)
    sum_outcomes_str = locale.format_string("%.2f", total_outcomes, grouping=True)
    final_str = locale.format_string("%.2f", final_balance, grouping=True)

    text_box.insert("end", f"Gesamteinnahmen: {sum_incomes_str} CHF\n")
    text_box.insert("end", f"Gesamtausgaben: {sum_outcomes_str} CHF\n")
    text_box.insert("end", f"Verbleibendes Guthaben: {final_str} CHF\n")

def close_app():
    app.destroy()

# ------------------------------
#   GUI-Einstellungen
# ------------------------------
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("Finanz-Tracker (Dark Mode)")
app.geometry("800x650")  # Größeres Fenster

app.configure(fg_color="#2B2B2B")

# Logo größer (150×150)
try:
    logo_img = Image.open("logo.png").resize((300,300))
    logo_ctk = ImageTk.PhotoImage(logo_img)
    label_logo = ctk.CTkLabel(app, image=logo_ctk, text="")
    label_logo.pack(pady=10)
except Exception as e:
    print("Kein Logo gefunden oder Fehler beim Laden:", e)

label_title = ctk.CTkLabel(app, text="Willkommen zum Finanz-Tracker!", font=("Consolas", 20))
label_title.pack(pady=10)

# Frame für Eingaben
frame_inputs = ctk.CTkFrame(app, fg_color="#333333")
frame_inputs.pack(pady=10, padx=10)

# Typ (Einnahme/Ausgabe)
label_type = ctk.CTkLabel(frame_inputs, text="Typ (Einnahme/Ausgabe):", font=("Consolas", 12))
label_type.grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_type = ctk.CTkEntry(frame_inputs, placeholder_text="z.B. Einnahme", width=200)
entry_type.grid(row=0, column=1, padx=5, pady=5)

# Betrag
label_amount = ctk.CTkLabel(frame_inputs, text="Betrag in CHF:", font=("Consolas", 12))
label_amount.grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_amount = ctk.CTkEntry(frame_inputs, placeholder_text="z.B. 6'500.00", width=200)
entry_amount.grid(row=1, column=1, padx=5, pady=5)

# Kategorie
label_category = ctk.CTkLabel(frame_inputs, text="Kategorie:", font=("Consolas", 12))
label_category.grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry_category = ctk.CTkEntry(frame_inputs, placeholder_text="z.B. Lohn / Miete", width=200)
entry_category.grid(row=2, column=1, padx=5, pady=5)

# Button: Transaktion hinzufügen
btn_add = ctk.CTkButton(frame_inputs, text="Transaktion hinzufügen", command=add_tx)
btn_add.grid(row=3, column=0, columnspan=2, pady=10)

# Info-Label
label_info = ctk.CTkLabel(app, text="", text_color="green", font=("Consolas", 12))
label_info.pack()

# Button: Transaktionen anzeigen
btn_show = ctk.CTkButton(app, text="Transaktionen (PDF-Stil) anzeigen", command=show_all_transactions)
btn_show.pack(pady=10)

# Textbox für Ausgabe
text_box = ctk.CTkTextbox(app, width=780, height=350)
# Monospaced Font => Spalten perfekt untereinander
text_box.configure(font=("Consolas", 12))
text_box.pack(pady=5)

# Beenden-Button
btn_close = ctk.CTkButton(app, text="Beenden", command=close_app)
btn_close.pack(pady=20)

app.mainloop()
