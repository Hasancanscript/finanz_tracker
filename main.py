from database import (
    add_transaction, show_transactions, get_total_income, 
    get_total_expenses, get_balance, plot_expenses_by_category, 
    export_to_csv, export_to_pdf, filter_transactions_by_month
)

def add_multiple_expenses():
    print("\n🔹 Neue Ausgaben hinzufügen")
    print("Gib mehrere Ausgaben in einer Zeile ein (z. B.: Miete: 1500, Strom: 80, Krankenkasse: 350)")
    print("Oder drücke einfach Enter, um abzubrechen.")

    eingabe = input("💰 Deine Ausgaben: ").strip()
    if not eingabe:
        return  # Falls der Nutzer nichts eingibt, abbrechen

    # Mehrere Ausgaben verarbeiten
    ausgaben = eingabe.split(",")  # Trennen nach ","
    
    for ausgabe in ausgaben:
        try:
            kategorie, betrag = ausgabe.split(":")  # Trennen nach ":"
            kategorie = kategorie.strip()  # Leerzeichen entfernen
            betrag = float(betrag.strip())  # Betrag in Float umwandeln

            # Transaktion speichern
            add_transaction("Ausgabe", betrag, kategorie)
            print(f"✅ Transaktion gespeichert: {kategorie} - {betrag:.2f} CHF")

        except ValueError:
            print(f"❌ Fehler: Ungültige Eingabe bei '{ausgabe.strip()}'. Bitte richtig eingeben!")

def main_menu():
    while True:
        print("\n📊 **Finanz-Tracker Menü**")
        print("1️⃣ Neue Transaktion hinzufügen")
        print("2️⃣ Alle Transaktionen anzeigen")
        print("3️⃣ Einnahmen & Ausgaben zusammenfassen")
        print("4️⃣ Diagramm der Ausgaben nach Kategorie")
        print("5️⃣ Transaktionen als CSV exportieren")
        print("6️⃣ Transaktionen als PDF exportieren")
        print("7️⃣ Transaktionen nach Monat filtern")
        print("0️⃣ Beenden")

        choice = input("👉 Wähle eine Option: ")

        if choice == "1":
            typ = input("📌 Typ (Einnahme/Ausgabe): ").strip().capitalize()
            if typ == "Einnahme":
                betrag = float(input("💰 Betrag in CHF: "))
                kategorie = input("📂 Kategorie: ").strip()
                add_transaction("Einnahme", betrag, kategorie)
                print(f"✅ Transaktion gespeichert: {kategorie} - {betrag:.2f} CHF")
            elif typ == "Ausgabe":
                add_multiple_expenses()  # Mehrere Ausgaben in einer Zeile eingeben
            else:
                print("❌ Ungültiger Typ! Bitte 'Einnahme' oder 'Ausgabe' eingeben.")
        
        elif choice == "2":
            show_transactions()
        
        elif choice == "3":
            print("\n📊 **Finanzübersicht**")
            print(f"💰 Gesamteinnahmen: {get_total_income():.2f} CHF")
            print(f"💸 Gesamtausgaben: {get_total_expenses():.2f} CHF")
            print(f"💼 Aktueller Saldo: {get_balance():.2f} CHF")
        
        elif choice == "4":
            plot_expenses_by_category()
        
        elif choice == "5":
            print("📤 Exportiere Transaktionen als CSV...")
            export_to_csv()
            print("✅ CSV-Export abgeschlossen.")

        elif choice == "6":
            print("📤 Exportiere Transaktionen als PDF...")
            export_to_pdf()
            print("✅ PDF-Export abgeschlossen.")
        
        elif choice == "7":
            jahr = input("📅 Jahr (z.B. 2025): ").strip()
            monat = input("📅 Monat (1-12): ").strip()
            filter_transactions_by_month(jahr, monat)
        
        elif choice == "0":
            print("👋 Programm beendet. Bis bald!")
            break
        
        else:
            print("❌ Ungültige Eingabe. Bitte versuche es erneut.")

if __name__ == "__main__":
    main_menu()
