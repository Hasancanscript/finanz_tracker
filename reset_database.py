import sqlite3

# Verbindung zur Datenbank
conn = sqlite3.connect("finanz_tracker.db")
cursor = conn.cursor()

# ALLE Einträge aus der Tabelle "transactions" löschen
cursor.execute("DELETE FROM transactions")

# Änderungen speichern und Verbindung schließen
conn.commit()
conn.close()

print("✅ Alle gespeicherten Transaktionen wurden gelöscht!")
