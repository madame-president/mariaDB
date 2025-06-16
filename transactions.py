import sqlite3

conn = sqlite3.connect("transactions.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    cost REAL,
    amount REAL
)
""")

while True:
    date = input("Date entry (YYYY-MM-DD) or 'q' to quit: ")
    if date.lower() == 'q':
        break

    cost = input("Transaction cost: ")
    amount = input("Sats received: ")

    cursor.execute("INSERT INTO transactions (date, cost, amount) VALUES (?, ?, ?)",
                   (date, float(cost), float(amount)))

    conn.commit()
    print("✅ Log is up to date.\n")

conn.close()
print("All done. Transactions saved in transactions.db.")