import sqlite3

conn = sqlite3.connect('sensors_database.db')
curs=conn.cursor()

for row in curs.execute("SELECT * FROM Sensors_data WHERE date(timestamp) = date('2019-03-28')"):
    print (row)
