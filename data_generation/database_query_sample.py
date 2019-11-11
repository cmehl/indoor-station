import sqlite3

conn=sqlite3.connect('sensors_database.db')
curs=conn.cursor()

maxTemp = 27.6

print ("\nEntire database contents:\n")
for row in curs.execute("SELECT * FROM Sensors_data"):
    print (row)
    
print ("\nDatabase entries for a specific humidity value:\n")
for row in curs.execute("SELECT * FROM Sensors_data WHERE hum='58'"):
    print (row)
    
print ("\nDatabase entries where the temperature is above 21oC:\n")
for row in curs.execute("SELECT * FROM Sensors_data WHERE temp>21.0"):
    print (row)
    
print ("\nDatabase entries where the temperature is above x:\n")
for row in curs.execute("SELECT * FROM Sensors_data WHERE temp>(?)", (maxTemp,)):
    print (row)
