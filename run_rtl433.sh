#!/bin/bash
#  sudo apt-get update
#  sudo apt-get upgrade -y
#  sudo apt-get install rtl-433
#  sudo apt install python3-pip
#  pip install dash
#  pip install sqlite-web
#  git clone https://github.com/AlexandreCo/rpi_rtlsdr_weather_station.git
#
#  crontab -e
#  # start sqlite_web display server
#  @reboot ~/.local/bin/sqlite_web ~/data/weatherstation.sqlite -H 192.168.1.175 -r
#  # start weather_station display server
#  @reboot python3 ~/rpi_rtlsdr_weather_station/show_weather_station.py
#  # every 7 min try to get new data
#  */7 * * * *  ~/rpi_rtlsdr_weather_station/run_rtl433.sh
#


#touch /tmp/stop_rtl
mkdir -p ~/data/

if [ ! -f /tmp/stop_rtl ]
then
	# TFA-TwinPlus approximately evey 30 seconds
	/usr/bin/rtl_433 -F json -R 31 -T 90 -E quit | /usr/bin/python3 ~/rpi_rtlsdr_weather_station/ws2sqlite.py
	# Generic-Temperature approximately every 150 seconds
	/usr/bin/rtl_433 -F json -R 38 -T 180 -E quit | /usr/bin/python3 ~/rpi_rtlsdr_weather_station/ws2sqlite.py
	# Oregon-RTGR328N  approximately every 60 seconds
	/usr/bin/rtl_433 -F json -R 12 -T 90 -E quit | /usr/bin/python3 ~/rpi_rtlsdr_weather_station/ws2sqlite.py
else
	sleep 1
fi


