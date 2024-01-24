# -*- coding: utf-8 -*-
import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime as dt
from datetime import timedelta
import sqlite3
import json
import getpass

sqlite_ws_file = "/home/"+str(getpass.getuser())+"/data/weatherstation.sqlite"    # name of the sqlite database file
config_file =  "/home/"+str(getpass.getuser())+"/rpi_rtlsdr_weather_station/display.json"    # name of the json config file
table_ws_name = 'data'   # name of the table
index_col = 'id'
date_col = 'date' # name of the date column
time_col = 'time'# name of the time column
model_col = 'model' # name of the model column

app = dash.Dash(__name__)
app.config.update({})
server = app.server

print(dcc.__version__)

todate = dt.now()
fromdate = dt.now()-timedelta(weeks=2)


def querywslog(model_name,col,fromdate,todate,coef):
    timestamp = []
    t_ws = []
    rain_mm_ws = []

    conn = sqlite3.connect(sqlite_ws_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM {tn} WHERE {mc} like '%{ma}%' AND {dc} BETWEEN '{fd}' AND '{td}' AND {cn} != \"\"". \
          format(tn=table_ws_name, dc=date_col, fd=fromdate, td=todate, mc=model_col, ma=model_name, cn=col))
    rows = c.fetchall()
    for row in rows:
        timestamp.append(row["date"] + " " + row["time"])
        t_ws.append(row[col]*coef)
    conn.close()
    return {'timestamp':timestamp, 'ws':t_ws}

def calc_rain_per_day(timestamp,rain):
    i=0
    format = "%Y-%m-%d %H:%M:%S"
    startrain = rain[0]
    datestamp = []
    rain_per_day=[]
    for ts in timestamp:
        if i>0:
            dt_object_prev = dt.strptime(timestamp[i-1], format)
            dt_object = dt.strptime(ts, format)
            if dt_object.date() > dt_object_prev.date():
                #print(dt_object_prev.date(), rain[i]- startrain)
                datestamp.append(dt_object_prev.date())
                if rain[i] < startrain: # we got a reset
                    startrain = rain[i]
                rain_per_day.append(round(rain[i]- startrain,1))
                startrain = rain[i]
        i=i+1
    return{'datestamp':datestamp, 'rain_per_day':rain_per_day}

def calc_rain_per_hour(timestamp,rain):
    i=0
    format = "%Y-%m-%d %H:%M:%S"
    startrain = rain[0]
    datestamp = []
    rain_per_hour=[]
    for ts in timestamp:
        if i>0:
            dt_object_prev = dt.strptime(timestamp[i-1], format)
            dt_object = dt.strptime(ts, format)

            hour = dt_object.replace(minute=0, second=0)
            prev_hour = dt_object_prev.replace(minute=0, second=0)
            if hour != prev_hour:
                # new hour
                #print("hour", dt_object_prev, rain[i] - startrain)
                datestamp.append(dt_object_prev)
                if rain[i] < startrain:  # we got a reset
                    startrain = rain[i]
                rain_per_hour.append(round(rain[i] - startrain, 1))
                startrain = rain[i]
        i=i+1
    return{'datestamp':datestamp, 'rain_per_hour':rain_per_hour}


def getMaxSubplot(filename):

    file = open(filename, 'r')

    max_col = 0
    max_row = 0
    for line in file:
        d = json.loads(line)
        col = d['col']
        row = d['row']
        if(col>max_col):
            max_col=col
        if(row>max_row):
            max_row=row
        print(col, row,max_row,max_col)

    file.close()
    return max_row+1,max_col


def create_figure_ws(figdatestart,figdateend):
    fromdate = dt.strptime(figdatestart[0:10], '%Y-%m-%d')
    todate = dt.strptime(figdateend[0:10], '%Y-%m-%d')


    max_row,max_col=getMaxSubplot(config_file)
    print( max_row,max_col)
    fig = make_subplots(rows=max_row, cols=max_col)

    file1 = open(config_file, 'r')
    for line in file1:

        d = json.loads(line)
        model = d['model']
        id  = d['id']
        type = d['type']
        src = d['src']
        name = d['name']
        col = d['col']
        row = d['row']
        coef = d['coef']

        print(model,src,col,row)
        dws = querywslog(model,src,fromdate,todate,coef)
        # add traces

        if(type == 1 ):
            fig.add_trace(
                go.Scatter(x=dws['timestamp'], y=dws['ws'], mode='lines', name=model),
                row=row, col=col
            )
        elif (type == 2):
            rph = calc_rain_per_hour(dws['timestamp'], dws['ws'])
            mname = 'rain ' + model
            fig.add_trace(
                go.Bar(x=rph['datestamp'], y=rph['rain_per_hour'], text=rph['rain_per_hour'], name=model, marker_color='blue'),
                row=row, col=col
            )
        elif (type == 3):
            rpd = calc_rain_per_day(dws['timestamp'],dws['ws'])
            mname = 'rain ' + model
            fig.add_trace(
                go.Bar(x=rpd['datestamp'], y=rpd['rain_per_day'], text=rpd['rain_per_day'], name=model, marker_color='blue'),
                row=row, col=col
            )
        # Update yaxis properties
        fig.update_yaxes(title_text=name, row=row, col=col)

    fig.update_layout(height=800,
        title_text='log - {:s} - {:s}'.format(fromdate.strftime("%-d %B %Y"), todate.strftime("%-d %B %Y")),
        paper_bgcolor="LightSteelBlue",
        showlegend=True, legend=dict(x=0,y=0),margin=dict(l=0, r=0, t=50, b=0))

    return(fig)

def serve_layout():
    return html.Div(children=[
        dcc.Graph(id='my-graph-1'),
        html.Div([
            dcc.DatePickerRange(
            id='date-picker-range-1',
            display_format='DD MMM YYYY',
            start_date=dt.now()-timedelta(weeks=2),
            end_date=dt.now()
        ),
    ], style={'text-align': 'center', 'background-color':'LightSteelBlue'}),     
])

app.layout = serve_layout

@app.callback(
    dash.dependencies.Output('my-graph-1', 'figure'),
    [dash.dependencies.Input('date-picker-range-1', 'start_date'),
     dash.dependencies.Input('date-picker-range-1', 'end_date')])

def update_output(start_date, end_date):

    return create_figure_ws(start_date, end_date)


if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0')

