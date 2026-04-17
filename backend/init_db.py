import sqlite3

conn = sqlite3.connect("complaints.db")
cursor = conn.cursor()

# पुराना complaints table हटाओ
cursor.execute("DROP TABLE IF EXISTS complaints")

# नया complaints table बनाओ (lat/lng columns added)
cursor.execute("""
    CREATE TABLE complaints(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        area TEXT,
        complaint TEXT,
        category TEXT,
        sentiment TEXT,
        urgency TEXT,
        status TEXT,
        language TEXT,
        emotion TEXT,
        department TEXT,
        assigned_officer TEXT,
        photo TEXT,
        voice TEXT,
        lat REAL,
        lng REAL
    )
""")

# Officers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS officers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    department TEXT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# Seed officers (demo accounts)
cursor.execute("INSERT OR IGNORE INTO officers (name, department, username, password) VALUES (?, ?, ?, ?)",
               ("Arpita", "PWD", "arpita95404@gmail.com", "1234"))
cursor.execute("INSERT OR IGNORE INTO officers (name, department, username, password) VALUES (?, ?, ?, ?)",
               ("Dipti", "Jal Nigam", "diptiyadavfzd123@gmail.com", "7896"))
cursor.execute("INSERT OR IGNORE INTO officers (name, department, username, password) VALUES (?, ?, ?, ?)",
               ("Vipin", "Police", "vipinn9920@gmail.com", "4561"))

conn.commit()
conn.close()
print("Complaints + Officers tables recreated successfully (lat/lng added)")
