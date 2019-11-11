import sqlite3

conn = sqlite3.connect('sensors_database.db')
curs=conn.cursor()

print ("\nLast Data logged on database:\n")
for row in curs.execute("SELECT * FROM Sensors_data"):
    print (row)
