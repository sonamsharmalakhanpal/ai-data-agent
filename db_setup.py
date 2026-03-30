import sqlite3

# Create/connect DB
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    company TEXT,
    country TEXT
)
""")

cursor.execute("""
CREATE TABLE deals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    amount INTEGER,
    stage TEXT,
    created_at TEXT
)
""")

# Insert sample data
cursor.executemany("INSERT INTO customers (name, company, country) VALUES (?, ?, ?)", [
    ("John", "ABC Corp", "USA"),
    ("Raj", "XYZ Ltd", "India"),
    ("Emma", "TechSoft", "UK")
])

cursor.executemany("INSERT INTO deals (customer_id, amount, stage, created_at) VALUES (?, ?, ?, ?)", [
    (1, 5000, "closed", "2024-01-01"),
    (2, 3000, "pipeline", "2024-02-01"),
    (1, 7000, "closed", "2024-03-01"),
    (3, 9000, "closed", "2024-04-01")
])

# Save & close
conn.commit()
conn.close()

print("Database created successfully!")