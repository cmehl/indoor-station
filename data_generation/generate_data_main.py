#!/usr/bin/python
# coding=utf-8
from __future__ import print_function
import serial, struct, sys, time
import sqlite3
import Adafruit_DHT

#----------------------------------------------
# DHT22 functions
#----------------------------------------------

# get data from DHT sensor
def getDHTdata():   
    DHT22Sensor = Adafruit_DHT.DHT22
    DHTpin = 17
    hum, temp = Adafruit_DHT.read_retry(DHT22Sensor, DHTpin)
    if hum is not None and temp is not None:
        hum = round(hum)
        temp = round(temp, 1)   
    return temp, hum


#----------------------------------------------
# SDS011 functions
#----------------------------------------------

DEBUG = 0
CMD_MODE = 2
CMD_QUERY_DATA = 4
CMD_DEVICE_ID = 5
CMD_SLEEP = 6
CMD_FIRMWARE = 7
CMD_WORKING_PERIOD = 8
MODE_ACTIVE = 0
MODE_QUERY = 1

ser = serial.Serial()
ser.port = "/dev/ttyUSB0"
ser.baudrate = 9600

ser.open()
ser.flushInput()

byte, data = 0, ""

def dump(d, prefix=''):
    print(prefix + ' '.join(x.encode('hex') for x in d))

def construct_command(cmd, data=[]):
    assert len(data) <= 12
    data += [0,]*(12-len(data))
    checksum = (sum(data)+cmd-2)%256
    ret = "\xaa\xb4" + chr(cmd)
    ret += ''.join(chr(x) for x in data)
    ret += "\xff\xff" + chr(checksum) + "\xab"

    if DEBUG:
        dump(ret, '> ')
    return ret

def process_data(d):
    r = struct.unpack('<HHxxBB', d[2:])
    pm25 = r[0]/10.0
    pm10 = r[1]/10.0
    checksum = sum(ord(v) for v in d[2:8])%256
    return [pm25, pm10]
    #print("PM 2.5: {} μg/m^3  PM 10: {} μg/m^3 CRC={}".format(pm25, pm10, "OK" if (checksum==r[2] and r[3]==0xab) else "NOK"))

def process_version(d):
    r = struct.unpack('<BBBHBB', d[3:])
    checksum = sum(ord(v) for v in d[2:8])%256
    print("Y: {}, M: {}, D: {}, ID: {}, CRC={}".format(r[0], r[1], r[2], hex(r[3]), "OK" if (checksum==r[4] and r[5]==0xab) else "NOK"))

def read_response():
    byte = 0
    while byte != "\xaa":
        byte = ser.read(size=1)

    d = ser.read(size=9)

    if DEBUG:
        dump(d, '< ')
    return byte + d

def cmd_set_mode(mode=MODE_QUERY):
    ser.write(construct_command(CMD_MODE, [0x1, mode]))
    read_response()

def cmd_query_data():
    ser.write(construct_command(CMD_QUERY_DATA))
    d = read_response()
    values = []
    if d[1] == "\xc0":
        values = process_data(d)
    return values

def cmd_set_sleep(sleep=1):
    mode = 0 if sleep else 1
    ser.write(construct_command(CMD_SLEEP, [0x1, mode]))
    read_response()

def cmd_set_working_period(period):
    ser.write(construct_command(CMD_WORKING_PERIOD, [0x1, period]))
    read_response()

def cmd_firmware_ver():
    ser.write(construct_command(CMD_FIRMWARE))
    d = read_response()
    process_version(d)

def cmd_set_id(id):
    id_h = (id>>8) % 256
    id_l = id % 256
    ser.write(construct_command(CMD_DEVICE_ID, [0]*10+[id_l, id_h]))
    read_response()


#----------------------------------------------
# SQL functions
#----------------------------------------------

# log sensor data on database
def logData(dbname,temp, hum, pm25, pm10):    
    conn=sqlite3.connect(dbname)
    curs=conn.cursor()
    curs.execute("INSERT INTO Sensors_data values(datetime('now','localtime'), (?), (?), (?), (?))", (temp, hum, pm25, pm10))
    conn.commit()
    conn.close()

#----------------------------------------------
# Main
#----------------------------------------------

if __name__ == "__main__":

    # Database
    dbname='sensors_database.db'

    sampleFreq = 10*60 # time in seconds

    # Main loop
    while True:

        # First step: we wake up the SDS011 sensors and
        # make a few measures to warm it (else the measures are wrong)
        # Approximate length is 1min
        cmd_set_sleep(0)
        cmd_set_mode(1);
        for t in range(30):
            values = cmd_query_data();
            try:
                pm25 = values[0]
                pm10 = values[1]
            except Exception:
                print("WARNING: exception caught.")
            time.sleep(2)

        # Second step: we read DHT22 data
        temp, hum = getDHTdata()

        # Third step: we add values to SQL database
        logData(dbname, temp, hum, pm25, pm10)

        # Setting the SDS sensor to sleep and waiting 
        cmd_set_mode(0);
        cmd_set_sleep()
        time.sleep(sampleFreq-60) # We take away 1min because of SDS measurements




