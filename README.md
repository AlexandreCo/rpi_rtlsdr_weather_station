# rpi_rtlsdr_weather_station
This project forked from https://github.com/AgriVision/rpi_rtlsdr_weather_station for my own weather station configuration


rpi_rtlsdr_weather_station provides  python code, based on https://dash.plotly.com to show weather data from a wireless weather station to a web page, served from a raspberry pi. Wireless data from the weather station is received with a RTL-SDR dongle and decoded by https://github.com/merbanan/rtl_433/.

The code is tested with a Inovalley kw9015b wireless rain meter a generic thermometer sensor and a Oregon thermometer


## The setup consists of two python scripts:
* <span>ws2sqlite.py</span> (pipes weather data from rtl_433 to a sqlite database)
* show_weather_station.py (serves a web page graphing data from the sqlite database using Dash.plotly)

## Installation
```
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install rtl-433
sudo apt install python3-pip
pip install dash
pip install sqlite-web
git clone https://github.com/AlexandreCo/rpi_rtlsdr_weather_station.git

```

Open the crontab editor:
```
crontab -e
```
Add the folowing lines to your crontab (replace the ip address with the ip of the machine) :

```
# start sqlite_web display server at boot time
@reboot ~/.local/bin/sqlite_web data/weatherstation.sqlite -H 192.168.1.175 -r

# start weather_station display server at boot time
@reboot python3 ~/rpi_rtlsdr_weather_station/show_weather_station.py

# every 7 min try to get new data
#  */7 * * * *  ~/rpi_rtlsdr_weather_station/run_rtl433.sh
```
The command is executed at an interval of 7 minutes.

The rtl_433 options used are:
Option | Description
------ | ------
-F json | output json format
-R 31 | only output protocol 31 (TFA-TwinPlus)
-R 38 | only output protocol 38 (Generic-Temperature)
-R 12 | only output protocol 12 (Oregon)
-T 90 | timeout if nothing received in 90 seconds for TFA-TwinPlus and Oregon-RTGR328N
-T 180 | timeout if nothing received in 180 seconds for  Generic-Temperature sensor
-E quit | quit command after successful event

The output (json data) is piped to the <span>ws2sqlite.py</span> script, which saves the data in a sqlite database.

## Web server 

The show_weather_station.py python script extracts the saved weather data from the sqlite database and displays nice graphs in a web browser. Dash.plotly is the framework used for this. A Dash DatePickerRange is used at the bottom of the page to select the dates for which the weather data is plotted. In this example the internal DASH webserver is used, but Dash can also be used in connection with your standard raspberri pi webserver such as apache2. When running standalone the web page is served at port 8050.


```
python3 rpi_rtlsdr_weather_station/show_weather_station.py
```

```
2.0.0
Dash is running on http://0.0.0.0:8050/

 * Serving Flask app 'show_weather_station' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on all addresses.
   WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://192.168.2.212:8050/ (Press CTRL+C to quit)
127.0.0.1 - - [30/Nov/2021 20:16:15] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [30/Nov/2021 20:16:15] "GET /_dash-layout HTTP/1.1" 200 -
127.0.0.1 - - [30/Nov/2021 20:16:15] "GET /_dash-dependencies HTTP/1.1" 200 -
127.0.0.1 - - [30/Nov/2021 20:16:15] "GET /_dash-component-suites/dash/dcc/async-graph.js HTTP/1.1" 304 -
127.0.0.1 - - [30/Nov/2021 20:16:15] "GET /_dash-component-suites/dash/dcc/async-datepicker.js HTTP/1.1" 304 -
127.0.0.1 - - [30/Nov/2021 20:16:15] "GET /_dash-component-suites/dash/dcc/async-plotlyjs.js HTTP/1.1" 304 -
127.0.0.1 - - [30/Nov/2021 20:16:18] "POST /_dash-update-component HTTP/1.1" 200 -
```

This project forked from https://github.com/AgriVision/rpi_rtlsdr_weather_station
More information can be found on: https://www.agri-vision.nl/portal/projects/25-rtl-sdr-based-weather-station-on-raspberry-pi

That's it!
