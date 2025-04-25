import sqlite3
import datetime
import locale
import os
import customtkinter as ctk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from fpdf import FPDF

# ----------------------------
# Datenbank-Funktionen
# ----------------------------
def init_db():
    if not os.path.exists("finanz_tracker.db"):
        with sqlite3.connect("finanz_tracker.db") as conn:
            conn.execute("""
                CREATE TABLE transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )


def add_transaction(ttype, amount, category):
    with sqlite3.connect("finanz_tracker.db") as conn:
        conn.execute(
            "INSERT INTO transactions (type, amount, category) VALUES (?, ?, ?)",
            (ttype, amount, category)
        )


def get_all_transactions():
    with sqlite3.connect("finanz_tracker.db") as conn:
        return conn.execute(
            "SELECT id, type, amount, category, date FROM transactions ORDER BY id DESC"
        ).fetchall()


def delete_all_transactions():
    with sqlite3.connect("finanz_tracker.db") as conn:
        conn.execute("DELETE FROM transactions")

# ----------------------------
# Formatierungs-Hilfen
# ----------------------------
locale.setlocale(locale.LC_NUMERIC, "de_CH.UTF-8")

def chf_format(x):
    return f"CHF {locale.format_string('%.2f', x, grouping=True)}"

def format_date(ds):
    return datetime.datetime.strptime(ds, "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y %H:%M")

# ----------------------------
# GUI-Aktionen
# ----------------------------
def refresh_entries():
    rows = get_all_transactions()
    inc_rows = [r for r in rows if r[1] == "Einnahme"]
    exp_rows = [r for r in rows if r[1] == "Ausgabe"]

    incomes_tree.delete(*incomes_tree.get_children())
    expenses_tree.delete(*expenses_tree.get_children())

    for idx, (rid, typ, amt, cat, dt) in enumerate(inc_rows):
        tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
        incomes_tree.insert(
            "", "end",
            values=(rid, typ, cat, chf_format(amt), format_date(dt)),
            tags=(tag,)
        )
    for idx, (rid, typ, amt, cat, dt) in enumerate(exp_rows):
        tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
        expenses_tree.insert(
            "", "end",
            values=(rid, typ, cat, chf_format(amt), format_date(dt)),
            tags=(tag,)
        )

    # Live-Stats
    total_in = sum(r[2] for r in inc_rows)
    total_out = sum(r[2] for r in exp_rows)
    cnt_in = len(inc_rows)
    cnt_out = len(exp_rows)
    balance = total_in - total_out

    count_label.configure(text=f"Einnahmen: {cnt_in} | Ausgaben: {cnt_out}")
    summary_label.configure(text=f"Total Ein: {chf_format(total_in)} | Total Ausg: {chf_format(total_out)}")
    balance_label.configure(text=f"Guthaben: {chf_format(balance)}")

# ----------------------------
def on_add():
    try:
        amt = float(entry_amount.get().replace(",", "."))
    except ValueError:
        return messagebox.showerror("Fehler", "Ungültiger Betrag")
    cat = entry_category.get().strip()
    if not cat:
        return messagebox.showerror("Fehler", "Kategorie fehlt")
    add_transaction(type_menu.get(), amt, cat)
    entry_amount.delete(0, ctk.END)
    entry_category.delete(0, ctk.END)
    refresh_entries()

# ----------------------------
def on_export_pdf():
    rows = get_all_transactions()
    if not rows:
        return messagebox.showinfo("Info", "Keine Daten")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Finanz-Tracker Übersicht", ln=1, align="C")
    pdf.ln(5)
    cols = ["ID", "Typ", "Kategorie", "Betrag", "Datum"]
    widths = [50, 120, 300, 100, 120]
    pdf.set_font("Helvetica", "B", 10)
    for w, col in zip(widths, cols):
        pdf.cell(w, 8, col, 1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 10)
    for rid, typ, amt, cat, dt in rows:
        pdf.cell(widths[0], 8, str(rid), 1)
        pdf.cell(widths[1], 8, typ, 1)
        pdf.cell(widths[2], 8, cat, 1)
        pdf.cell(widths[3], 8, chf_format(amt), 1, align="R")
        pdf.cell(widths[4], 8, format_date(dt), 1)
        pdf.ln()
    filename = f"finanz_{datetime.datetime.now():%Y%m%d_%H%M%S}.pdf"
    pdf.output(filename)
    messagebox.showinfo("Erfolg", f"PDF gespeichert als {filename}")

# ----------------------------
# GUI-Aufbau
# ----------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
app = ctk.CTk()
app.title("Finanz-Tracker 360")
app.geometry("950x850")

# Style für Treeviews
style = ttk.Style(app)
style.theme_use("clam")
style.configure(
    "Custom.Treeview",
    background="#1e1e1e", fieldbackground="#1e1e1e",
    foreground="#e0e0e0", font=("Consolas", 11), rowheight=36,
    borderwidth=0, highlightthickness=0
)
style.configure(
    "Custom.Treeview.Heading",
    background="#272727", foreground="#ffffff",
    font=("Consolas", 12, "bold"), borderwidth=0
)
style.layout("Custom.Treeview", [('Custom.Treeview.treearea', {'sticky': 'nswe'})])
style.map(
    "Custom.Treeview",
    background=[('selected', '#3a6ea5')],
    foreground=[('selected', 'white')]
)

# Header
try:
    img = Image.open("logo.png").resize((80, 80))
    logo = ImageTk.PhotoImage(img)
    ctk.CTkLabel(app, image=logo, text="").pack(pady=5)
except:
    pass
ctk.CTkLabel(app, text="Finanz-Tracker 360", font=("Consolas", 26, "bold")).pack(pady=5)

# Eingabe-Container
frm = ctk.CTkFrame(app, corner_radius=12, fg_color="#272727")
frm.pack(padx=30, pady=20, fill="x")
ctk.CTkLabel(frm, text="Typ:", width=100).grid(row=0, column=0, sticky="w", padx=10)
type_menu = ctk.CTkOptionMenu(frm, values=["Einnahme", "Ausgabe"], width=180)
type_menu.set("Einnahme")
type_menu.grid(row=0, column=1, sticky="w", padx=10)
ctk.CTkLabel(frm, text="Betrag:", width=100).grid(row=1, column=0, sticky="w", padx=10)
entry_amount = ctk.CTkEntry(frm, placeholder_text="z.B. 1500.00", width=180)
entry_amount.grid(row=1, column=1, sticky="w", padx=10)
ctk.CTkLabel(frm, text="Kategorie:", width=100).grid(row=2, column=0, sticky="w", padx=10)
entry_category = ctk.CTkEntry(frm, placeholder_text="z.B. Miete", width=260)
entry_category.grid(row=2, column=1, sticky="w", padx=10)

# Action-Buttons
btn_frame = ctk.CTkFrame(app, corner_radius=12, fg_color="#272727")
btn_frame.pack(padx=30, pady=(0,20), fill="x")
ctk.CTkButton(btn_frame, text="Hinzufügen", corner_radius=8, command=on_add).pack(side="left", padx=15, pady=10)
ctk.CTkButton(btn_frame, text="Export PDF", corner_radius=8, command=on_export_pdf).pack(side="left", padx=15)
ctk.CTkButton(btn_frame, text="Alle löschen", corner_radius=8, fg_color="#b3372c", hover_color="#cf4427", command=lambda: (delete_all_transactions(), refresh_entries())).pack(side="left", padx=15)

# Live-Stats oberhalb der Tabellen
count_label = ctk.CTkLabel(app, text="Einnahmen: 0 | Ausgaben: 0", font=("Consolas",12))
summary_label = ctk.CTkLabel(app, text="Total Ein: CHF 0.00 | Total Ausg: CHF 0.00", font=("Consolas",12))
balance_label = ctk.CTkLabel(app, text="Guthaben: CHF 0.00", text_color="#00b894", font=("Consolas",14,"bold"))
count_label.pack(pady=(10,5))
summary_label.pack()
balance_label.pack(pady=(5,20))

# Einnahmen-Tabelle
ctk.CTkLabel(app, text="Einnahmen", text_color="#00b894", font=("Consolas",18,"bold")).pack(pady=(10,0))
incomes_frame = ctk.CTkFrame(app, fg_color="#1e1e1e")
incomes_frame.pack(padx=30, pady=10, fill="both", expand=True)
incomes_tree = ttk.Treeview(incomes_frame, style="Custom.Treeview", columns=("ID","Typ","Kategorie","Betrag","Datum"), show="headings", height=6)
# Spalten-Ausrichtung und -Breite
incomes_tree.heading("ID", text="ID", anchor="center")
incomes_tree.column("ID", width=50, anchor="center", stretch=False)
incomes_tree.heading("Typ", text="Typ", anchor="w")
incomes_tree.column("Typ", width=120, anchor="w", stretch=False)
incomes_tree.heading("Kategorie", text="Kategorie", anchor="w")
incomes_tree.column("Kategorie", width=300, anchor="w", stretch=False)
incomes_tree.heading("Betrag", text="Betrag", anchor="w")
incomes_tree.column("Betrag", width=160, anchor="w", stretch=False)
incomes_tree.heading("Datum", text="Datum", anchor="w")
incomes_tree.column("Datum", width=200, anchor="w", stretch=True)
incomes_tree.pack(fill="both", expand=True)
scroll_in = ttk.Scrollbar(incomes_frame, orient="vertical", command=incomes_tree.yview)
incomes_tree.configure(yscrollcommand=scroll_in.set)
scroll_in.pack(side="right", fill="y")

# Ausgaben-Tabelle
ctk.CTkLabel(app, text="Ausgaben", text_color="#d63031", font=("Consolas",18,"bold")).pack(pady=(10,0))
expenses_frame = ctk.CTkFrame(app, fg_color="#1e1e1e")
expenses_frame.pack(padx=30, pady=10, fill="both", expand=True)
expenses_tree = ttk.Treeview(expenses_frame, style="Custom.Treeview", columns=("ID","Typ","Kategorie","Betrag","Datum"), show="headings", height=6)
# Gleiche Spalten wie Einnahmen
expenses_tree.heading("ID", text="ID", anchor="center")
expenses_tree.column("ID", width=50, anchor="center", stretch=False)
expenses_tree.heading("Typ", text="Typ", anchor="w")
expenses_tree.column("Typ", width=120, anchor="w", stretch=False)
expenses_tree.heading("Kategorie", text="Kategorie", anchor="w")
expenses_tree.column("Kategorie", width=300, anchor="w", stretch=False)
expenses_tree.heading("Betrag", text="Betrag", anchor="w")
expenses_tree.column("Betrag", width=160, anchor="w", stretch=False)
expenses_tree.heading("Datum", text="Datum", anchor="w")
expenses_tree.column("Datum", width=200, anchor="w", stretch=True)
expenses_tree.pack(fill="both", expand=True)
scroll_out = ttk.Scrollbar(expenses_frame, orient="vertical", command=expenses_tree.yview)
expenses_tree.configure(yscrollcommand=scroll_out.set)
scroll_out.pack(side="right", fill="y")

# Start
delete_all_transactions()
refresh_entries()
app.mainloop()
