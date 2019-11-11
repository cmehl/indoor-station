from datetime import datetime, timedelta
import matplotlib.dates as mdates

import numpy as np
import io

from flask import Flask, render_template, send_file, make_response, request, Markup
app = Flask(__name__)

import sqlite3
conn=sqlite3.connect('../data_generation/sensors_database.db')
curs=conn.cursor()

import plotting_routines as pltr

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

# Retrieve LAST data from database
def getLastData():
    for row in curs.execute("SELECT * FROM Sensors_data ORDER BY timestamp DESC LIMIT 1"):
        # adding one hour because database is in UTC
        fmt = '%Y-%m-%d %H:%M:%S'
        time = str(datetime.strptime(row[0], fmt)) # + timedelta(hours=1))
        temp = row[1]
        hum = row[2]
        pm25 = row[3]
        pm10 = row[4]
	#conn.close()
    return time, temp, hum, pm25, pm10

# Get 'x' samples of historical data
def getHistData(numSamples):
    curs.execute("SELECT * FROM Sensors_data ORDER BY timestamp DESC LIMIT "+str(numSamples))
    data = curs.fetchall()
    dates = []
    temps = []
    hums = []
    pm25s = []
    pm10s = []
    for row in reversed(data):
        # adding one hour because database is in UTC
        fmt = '%Y-%m-%d %H:%M:%S'
        time = str(datetime.strptime(row[0], fmt)) # + timedelta(hours=1))
        dates.append(time)
        temps.append(row[1])
        hums.append(row[2])
        pm25s.append(row[3])
        pm10s.append(row[4])
        temps, hums = testData(temps, hums)
    return dates, temps, hums, pm25s, pm10s

# Test data for cleanning possible "out of range" values
def testData(temps, hums):
    n = len(temps)
    # Checking range of values
    for i in range(0, n-1):
        # Treat the None cases
        if temps[i]==None:
            temps[i] = temps[i-2]
        if hums[i]==None:
            hums[i] = hums[i-2]

        if (temps[i] < 10 or temps[i] >40):
            temps[i] = temps[i-2]
        if (hums[i] < 20 or hums[i] >100):
            hums[i] = hums[i-2]

    return temps, hums


# Get Max number of rows (table size)
def maxRowsTable():
	for row in curs.execute("select COUNT(temp) from Sensors_data"):
		maxNumberRows=row[0]
	return maxNumberRows

# Get sample frequency in minutes
def freqSample():
	times, temps, hums, pm25s, pm10s = getHistData(2)
	fmt = '%Y-%m-%d %H:%M:%S'
	tstamp0 = datetime.strptime(times[0], fmt)
	tstamp1 = datetime.strptime(times[1], fmt)
	freq = tstamp1-tstamp0
	freq = int(round(freq.total_seconds()/60))
	return (freq)


def getDayAvgData(rangeDays):

  dates = []
  temps_avg = []
  hums_avg = []
  pm25s_avg = []
  pm10s_avg = []
  #
  temps_rms = []
  hums_rms = []
  pm25s_rms = []
  pm10s_rms = []

  todays_date = datetime.now()
  
  for i in range(rangeDays+1):

    # Considered date
    date_current = (todays_date - timedelta(days=i)).strftime('%Y-%m-%d')

    # Initialize number of elements
    nb_elements = 0

    # Initialize current day averages
    temp_avg_cur = 0
    hum_avg_cur = 0
    pm25_avg_cur = 0
    pm10_avg_cur = 0

    # Initialize sum of squares
    sumsq_temp_cur = 0
    sumsq_hum_cur = 0
    sumsq_pm25_cur = 0
    sumsq_pm10_cur = 0

    # Loop over elements of given day in SQL database
    # Remark: averages and RMS are computed using a "naive" algorithm -> may be improved
    for row in curs.execute("SELECT * FROM Sensors_data WHERE date(timestamp) = date(?)", (date_current,)):
      # Making sure temperature and humidity have consistent values
      keep_data = True
      if (row[1]==None or row[2]==None):
        keep_data = False
      
      if keep_data==True:   # if it is not None we check that (else we would have an error) 
          if (row[1] < 10 or row[1] >40):
            keep_data = False
          if (row[2] < 20 or row[2] >100):
            keep_data = False

      # Updating number of elements
      if keep_data is True:
        nb_elements += 1
        # Updating averages
        temp_avg_cur += row[1]
        hum_avg_cur += row[2]
        pm25_avg_cur += row[3]
        pm10_avg_cur += row[4]
        # Updating sum of square
        sumsq_temp_cur += row[1]**2
        sumsq_hum_cur += row[2]**2
        sumsq_pm25_cur += row[3]**2
        sumsq_pm10_cur += row[4]**2

    # Divide by number of elements to get average
    if nb_elements==0:
      temp_avg_cur = None
      hum_avg_cur = None
      pm25_avg_cur = None
      pm10_avg_cur = None
      #
      temp_rms_cur = None
      hum_rms_cur = None
      pm25_rms_cur = None
      pm10_rms_cur = None
    else:
      # Divide by number of elements to get average
      temp_avg_cur /= nb_elements
      hum_avg_cur /= nb_elements
      pm25_avg_cur /= nb_elements
      pm10_avg_cur /= nb_elements
      # Get RMS using defintion
      temp_rms_cur = ((1.0/nb_elements)*(sumsq_temp_cur) - temp_avg_cur**2)**0.5
      hum_rms_cur = ((1.0/nb_elements)*(sumsq_hum_cur) - hum_avg_cur**2)**0.5
      pm25_rms_cur = ((1.0/nb_elements)*(sumsq_pm25_cur) - pm25_avg_cur**2)**0.5
      pm10_rms_cur = ((1.0/nb_elements)*(sumsq_pm10_cur) - pm10_avg_cur**2)**0.5
  

    # Fill resulting lists
    dates.append(date_current)
    temps_avg.append(temp_avg_cur)
    hums_avg.append(hum_avg_cur)
    pm25s_avg.append(pm25_avg_cur)
    pm10s_avg.append(pm10_avg_cur)
    #
    temps_rms.append(temp_rms_cur)
    hums_rms.append(hum_rms_cur)
    pm25s_rms.append(pm25_rms_cur)
    pm10s_rms.append(pm10_rms_cur)


  # We need to invert everything
  dates = dates[::-1]
  temps_avg = temps_avg[::-1]
  hums_avg = hums_avg[::-1]
  pm25s_avg = pm25s_avg[::-1]
  pm10s_avg = pm10s_avg[::-1]
  temps_rms = temps_rms[::-1]
  hums_rms = hums_rms[::-1]
  pm25s_rms = pm25s_rms[::-1]
  pm10s_rms = pm10s_rms[::-1]

  return dates, temps_avg, hums_avg, pm25s_avg, pm10s_avg, temps_rms, hums_rms, pm25s_rms, pm10s_rms

# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

# define and initialize global variables
global numSamples
numSamples = maxRowsTable()
if (numSamples > 101):
        numSamples = 100

global freqSamples
freqSamples = freqSample()

global rangeTime
rangeTime = 3
			
# =============================================================================
# FLASK ROUTINES
# =============================================================================	
		
# main route 
@app.route("/")
@app.route("/index")
def index():
	time, temp, hum, pm25, pm10 = getLastData()
	templateData = {
	  'time'		: time,
      'temp'		: temp,
      'hum'			: hum,
      'pm25'      : pm25,
      'pm10'      : pm10,
      'freq'		: freqSamples,
      'rangeTime'		: rangeTime
	}
	return render_template('index.html', **templateData)


@app.route("/historic_short_term", methods=['GET'])
def historic_short_term():
    global numSamples 
    global freqSamples
    global rangeTime
    # Maximal range time to look at set to 72h
    rangeTime = 72.0
    rangeTime_minutes = 60.0*rangeTime # Convert range in minutes to compute numSamples
    if (rangeTime_minutes < freqSamples):
        rangeTime_minutes = freqSamples + 1
    numSamples = rangeTime_minutes//freqSamples
    numMaxSamples = maxRowsTable()
    if (numSamples > numMaxSamples):
        numSamples = (numMaxSamples-1)
    
    plotly_graph_TH, plotly_graph_PM = pltr.plot_instant(numSamples)

    templateData = {
      'plotly_graph_TH'     : plotly_graph_TH,
      'plotly_graph_PM'     : plotly_graph_PM
	  }
    
    return render_template('historic_short_term.html', **templateData)
	

	
@app.route("/historic_long_term", methods=['GET'])
def historic_long_term():

  # Number of days to plot
  rangeDays = 30

  plotly_graph_TH, plotly_graph_PM = pltr.plot_avg(rangeDays)

  templateData = {
      'plotly_graph_TH'     : plotly_graph_TH,
      'plotly_graph_PM'     : plotly_graph_PM
  }

  return render_template('historic_long_term.html', **templateData)	



# =============================================================================
# MAIN PROGRAM
# =============================================================================
	
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=False)
