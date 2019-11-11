import sqlite3 as lite
import sys

con = lite.connect('sensors_database.db')

with con:
    
    cur = con.cursor() 
    cur.execute("DROP TABLE IF EXISTS Sensors_data")
    cur.execute("CREATE TABLE Sensors_data(timestamp DATETIME, temp NUMERIC, hum NUMERIC, pm25 NUMERIC, pm10 NUMERIC)")
