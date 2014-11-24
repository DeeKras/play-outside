from flask import Flask, render_template,request
from weather import SchoolWeather
import requests
import pygeoip
import datetime

rawdata = pygeoip.GeoIP('/home/deekras/PythonEnv/My work/Playoutside/GeoLiteCity.dat')
db = '/home/deekras/PythonEnv/PlayOutside/schools.db'

app = Flask (__name__)

def find_lnglat_by_ip():
    print 'x'
    ip = request.remote_addr
    if '127.0.0.1' == ip:
        ip = requests.get("http://icanhazip.com/").content
        data = rawdata.record_by_name(ip)

        lat = data['latitude']
        lng = data['longitude']
    return lat, lng

@app.route('/')
def display_firstpage():
   lat, lng = find_lnglat_by_ip()
   date = '{}T12:00:00-0400'.format(datetime.date.today())
   weather_for_city = SchoolWeather(lat, lng, date)
   pretty_place = ('{}, {} {} ({})').format(weather_for_city.city, weather_for_city.state, weather_for_city.country, weather_for_city.neighborhood)
   return render_template('firstpage.html', place = pretty_place)

app.run(debug = True)