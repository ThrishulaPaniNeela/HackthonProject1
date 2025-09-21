import sqlite3

conn = sqlite3.connect("civic_issues.db")
c = conn.cursor()

# Add photo column (run only once)
c.execute("ALTER TABLE issues ADD COLUMN photo TEXT")

conn.commit()
conn.close()
print("Photo column added successfully!")
