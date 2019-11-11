from datetime import datetime

import json
import plotly
import plotly.plotly as ply
import plotly.graph_objs as go

import appWebServerHistoric as appweb

# =============================================================================
# PLOTTING ROUTINES: INSTANTANEOUS VALUES
# =============================================================================
	
# Humidity and temperature
def plot_instant(numSamples):

    # GET THE DATA
    #-----------------------------------------------
    # Get values
    times, temps, hums, pm25s, pm10s = appweb.getHistData(numSamples)
     
    # Convert times in datatime object
    times_datetime = []
    fmt = '%Y-%m-%d %H:%M:%S'
    for time in times:
        times_datetime.append(datetime.strptime(time,fmt))

    # PLOT HUMIDITY AND TEMPERATURE
    #-----------------------------------------------
    # Data to plot
    trace_temp = go.Scatter(x= times_datetime, 
                            y=temps, 
                            name = 'Temperature (°C)',
                            mode='lines',
                            visible=True,
                            line = dict(
                                    color = ('rgb(222, 120, 30)'),
                                    width = 3))
    
    trace_hum = go.Scatter(x= times_datetime, 
                           y=hums, 
                           name = "Humidity (%)",
                           mode='lines',
                           visible=False,
                           line = dict(
                                    color = ('rgb(30, 120, 222)'),
                                    width = 3))
    
    
    data_TH = [trace_temp,trace_hum]
    
    # Buttons to select variable
    updatemenus_TH = list([
    dict(type="buttons",
         active=-1,
         buttons=list([
            dict(label = 'Temperature',
                 method = 'update',
                 args = [{'visible': [True, False]},
                         {'title': 'Temperature (°C)'}]),
            dict(label = 'Humidity',
                 method = 'update',
                 args = [{'visible': [False, True]},
                         {'title': 'Humidity (%)'}])
            ]),
        )
    ])


    # Layout
    layout_TH = dict(
    title='Temperature (°C)',
    updatemenus=updatemenus_TH,
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=6,
                     label='6h',
                     step='hour',
                     stepmode='backward'),
                dict(count=12,
                     label='12h',
                     step='hour',
                     stepmode='backward'),
                dict(count=24,
                    label='24h',
                    step='hour',
                    stepmode='todate'),
                dict(count=48,
                    label='48h',
                    step='hour',
                    stepmode='backward'),
                dict(count=72,
                    label='72h',
                    step='hour',
                    stepmode='backward')
            ])
        ),
        rangeslider=dict(
            visible = True
        ),
        type='date'
       )
    )
                               
    fig_TH = go.Figure(data=data_TH, layout=layout_TH)
    plot_TH = plotly.offline.plot(fig_TH, output_type='div', include_plotlyjs=False)


    # PLOT PM2.5 AND PM10
    #-----------------------------------------------
    # Data to plot
    trace_pm25 = go.Scatter(x= times_datetime, 
                            y=pm25s, 
                            name = 'PM2.5 (μg/m3)',
                            mode='lines',
                            visible=True,
                            line = dict(
                                    color = ('rgb(147, 11, 201)'),
                                    width = 3))
    
    trace_pm10 = go.Scatter(x= times_datetime, 
                           y=pm10s, 
                           name = "PM10 (μg/m3)",
                           mode='lines',
                           visible=False,
                           line = dict(
                                    color = ('rgb(65, 201, 11)'),
                                    width = 3))
    
    
    data_PM = [trace_pm25,trace_pm10]

    # Buttons to select variable
    updatemenus_PM = list([
    dict(type="buttons",
         active=-1,
         buttons=list([
            dict(label = 'PM2.5',
                 method = 'update',
                 args = [{'visible': [True, False]},
                         {'title': 'PM2.5 (μg/m3)'}]),
            dict(label = 'PM10',
                 method = 'update',
                 args = [{'visible': [False, True]},
                         {'title': 'PM10 (μg/m3)'}])
            ]),
        )
    ])


    # Layout
    layout_PM = dict(
    title='PM2.5 (μg/m3)',
    updatemenus=updatemenus_PM,
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=6,
                     label='6h',
                     step='hour',
                     stepmode='backward'),
                dict(count=12,
                     label='12h',
                     step='hour',
                     stepmode='backward'),
                dict(count=24,
                    label='24h',
                    step='hour',
                    stepmode='todate'),
                dict(count=48,
                    label='48h',
                    step='hour',
                    stepmode='backward'),
                dict(count=72,
                    label='72h',
                    step='hour',
                    stepmode='backward')
            ])
        ),
        rangeslider=dict(
            visible = True
        ),
        type='date'
       )
    )
                               
    fig_PM = go.Figure(data=data_PM, layout=layout_PM)
    plot_PM = plotly.offline.plot(fig_PM, output_type='div', include_plotlyjs=False)

    return plot_TH, plot_PM

# =============================================================================
# DAY AVERAGED VALUES PLOTTING ROUTINES
# =============================================================================

def plot_avg(rangeDays):

    # GET THE DATA
    #-----------------------------------------------
    # Get values
    dates, temps_avg, hums_avg, pm25s_avg, pm10s_avg, temps_rms, hums_rms, pm25s_rms, pm10s_rms = appweb.getDayAvgData(rangeDays)
       
    # Convert times in datatime object
    dates_datetime = []
    fmt = '%Y-%m-%d'
    for date in dates:
       dates_datetime.append(datetime.strptime(date,fmt))

    dates_datetime_rev = dates_datetime[::-1]

    # PLOT AVERAGE HUMIDITY AND TEMPERATURE
    #-----------------------------------------------
    # Used for filled plots
    temps_upper = []
    temps_lower = []
    hums_upper = []
    hums_lower = []
    for i in range(len(dates_datetime)):
        if temps_avg[i]==None:
            temps_upper.append(None)
            temps_lower.append(None)
            hums_upper.append(None)
            hums_lower.append(None)
        else:
            temps_upper.append(temps_avg[i] + temps_rms[i])
            temps_lower.append(max(0.0,temps_avg[i] - temps_rms[i]))
            hums_upper.append(hums_avg[i] + hums_rms[i])
            hums_lower.append(max(0.0,hums_avg[i] - hums_rms[i]))

    temps_lower = temps_lower[::-1]
    hums_lower = hums_lower[::-1]

    # Data to plot
    trace_temp = go.Scatter(x= dates_datetime, 
                            y=temps_avg, 
                            name = 'Temperature (°C)',
                            mode='lines',
                            visible=True,
                            line = dict(
                                    color = ('rgb(222, 120, 30)'),
                                    width = 3))
    
    trace_hum = go.Scatter(x= dates_datetime, 
                           y=hums_avg, 
                           name = "Humidity (%)",
                           mode='lines',
                           visible=False,
                           line = dict(
                                    color = ('rgb(30, 120, 222)'),
                                    width = 3))
    #
    trace_temp_filled = go.Scatter(x= dates_datetime+dates_datetime_rev, 
                            y=temps_upper+temps_lower, 
                            name = 'Temperature (°C)',
                            mode='lines',
                            fill='tozerox',
                            fillcolor='rgba(222, 120, 30,0.2)',
                            showlegend=False,
                            visible=True,
                            line = dict(
                                    color = ('rgba(255, 255, 255, 0)'))
                            )
    
    trace_hum_filled = go.Scatter(x= dates_datetime+dates_datetime_rev, 
                           y=hums_upper+hums_lower, 
                           name = "Humidity (%)",
                           mode='lines',
                           fill='tozerox',
                           fillcolor='rgba(30, 120, 222,0.2)',
                           showlegend=False,
                           visible=False,
                           line = dict(
                                    color = ('rgba(255, 255, 255, 0)'))
                           )
    
    
    data_TH = [trace_temp,trace_hum,trace_temp_filled,trace_hum_filled]
    
    # Buttons to select variable
    updatemenus_TH = list([
    dict(type="buttons",
         active=-1,
         buttons=list([
            dict(label = 'Temperature',
                 method = 'update',
                 args = [{'visible': [True, False]*2},
                         {'title': 'Temperature (°C)'}]),
            dict(label = 'Humidity',
                 method = 'update',
                 args = [{'visible': [False, True]*2},
                         {'title': 'Humidity (%)'}])
            ]),
        )
    ])


    # Layout
    layout_TH = go.Layout(
    title='Temperature (°C)',
    updatemenus=updatemenus_TH
    )
                               
    fig_TH = go.Figure(data=data_TH, layout=layout_TH)
    plot_TH = plotly.offline.plot(fig_TH, output_type='div', include_plotlyjs=False)


    # PLOT AVERAGE PM2.5 AND PM10
    #-----------------------------------------------
    # Used for filled plots
    pm25s_upper = []
    pm25s_lower = []
    pm10s_upper = []
    pm10s_lower = []
    for i in range(len(dates_datetime)):
        if pm25s_avg[i]==None or pm10s_avg[i]==None:
            pm25s_upper.append(None)
            pm25s_lower.append(None)
            pm10s_upper.append(None)
            pm10s_lower.append(None)
        else:
            pm25s_upper.append(pm25s_avg[i] + pm25s_rms[i])
            pm25s_lower.append(max(0.0,pm25s_avg[i] - pm25s_rms[i]))
            pm10s_upper.append(pm10s_avg[i] + pm10s_rms[i])
            pm10s_lower.append(max(0.0,pm10s_avg[i] - pm10s_rms[i]))

    pm25s_lower = pm25s_lower[::-1]
    pm10s_lower = pm10s_lower[::-1]

    # Data to plot
    trace_pm25 = go.Scatter(x= dates_datetime, 
                            y=pm25s_avg, 
                            name = 'PM2.5 (μg/m3)',
                            mode='lines',
                            visible=True,
                            line = dict(
                                    color = ('rgb(147, 11, 201)'),
                                    width = 3))
    
    trace_pm10 = go.Scatter(x= dates_datetime, 
                           y=pm10s_avg, 
                           name = "PM10 (μg/m3)",
                           mode='lines',
                           visible=False,
                           line = dict(
                                    color = ('rgb(65, 201, 11)'),
                                    width = 3))
    #
    trace_pm25_filled = go.Scatter(x= dates_datetime+dates_datetime_rev, 
                            y=pm25s_upper+pm25s_lower, 
                            name = 'PM2.5 (μg/m3)',
                            mode='lines',
                            fill='tozerox',
                            fillcolor='rgba(147, 11, 201,0.2)',
                            showlegend=False,
                            visible=True,
                            line = dict(
                                    color = ('rgba(255, 255, 255, 0)'))
                            )
    
    trace_pm10_filled = go.Scatter(x= dates_datetime+dates_datetime_rev, 
                           y=pm10s_upper+pm10s_lower, 
                           name = "PM10 (μg/m3)",
                           mode='lines',
                           fill='tozerox',
                           fillcolor='rgba(65, 201, 11,0.2)',
                           showlegend=False,
                           visible=False,
                           line = dict(
                                    color = ('rgba(255, 255, 255, 0)'))
                           )
    
    
    data_PM = [trace_pm25,trace_pm10,trace_pm25_filled,trace_pm10_filled]

    # Buttons to select variable
    updatemenus_PM = list([
    dict(type="buttons",
         active=-1,
         buttons=list([
            dict(label = 'PM2.5',
                 method = 'update',
                 args = [{'visible': [True, False]*2},
                         {'title': 'PM2.5 (μg/m3)'}]),
            dict(label = 'PM10',
                 method = 'update',
                 args = [{'visible': [False, True]*2},
                         {'title': 'PM10 (μg/m3)'}])
            ]),
        )
    ])


    # Layout
    layout_PM = dict(
    title='PM2.5 (μg/m3)',
    updatemenus=updatemenus_PM)
                               
    fig_PM = go.Figure(data=data_PM, layout=layout_PM)
    plot_PM = plotly.offline.plot(fig_PM, output_type='div', include_plotlyjs=False)

    return plot_TH, plot_PM
