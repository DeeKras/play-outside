from flask import Flask, render_template,request
from weather import SchoolWeather
# from search import find_lnglat_by_ip
import requests
import datetime
import pygeoip
import sqlite3

rawdata = pygeoip.GeoIP('/home/deekras/PythonEnv/My work/Playoutside/GeoLiteCity.dat')
db = '/home/deekras/PythonEnv/PlayOutside/schools.db'

def get_db_connection():
    conn = sqlite3.connect(db)
    conn.text_factory = str
    return conn

app = Flask (__name__)


@app.route('/weather', methods = ['GET','POST'])
def display_weather():
    print 'x'
    if request.method == 'GET':
        lat, lng = find_lnglat_by_ip()

    elif request.method == 'POST'   :
        if request.form['searchby'] == 'postal':
            lat, lng = find_lnglat_by_postal()
        elif request.form['searchby'] == 'place':
            lat, lng = find_lnglat_by_place()
        elif request.form['searchby'] == 'code':
            lat, lng = find_lnglat_by_code()
    
   
    date = '{}T12:00:00-0400'.format(datetime.date.today())

    weather_for_city = SchoolWeather(lat, lng, date)

    
    hourly =  weather_for_city.hourly
    display_date = weather_for_city.pretty_date
    place = '{}, {} {}'.format(weather_for_city.city, weather_for_city.state, weather_for_city.country)
 
    return render_template('weather.html', 
        place = place,
        display_date = display_date, 
        hourly = hourly)
	# return 'ready'

@app.route('/search',  methods = ['GET'])   
def display_searchpage():
    return render_template('search.html')
	
# ------------functions to search for lng/ lat  ------------------

def find_lnglat_by_ip():
    ip = request.remote_addr
    if '127.0.0.1' == ip:
        ip = requests.get("http://icanhazip.com/").content
        data = rawdata.record_by_name(ip)

        lat = data['latitude']
        lng = data['longitude']
    return lat, lng

def find_lnglat_by_postal():
    zipcode = request.form['postal']

    api = "http://api.zippopotam.us/us/{}".format(zipcode)
    json_response = requests.get(api).json()
    lng = json_response['places'][0]['longitude']
    lat = json_response['places'][0]['latitude']
    return lat, lng

def find_lnglat_by_place():
    state = request.form['state']
    city = request.form['postal']

    api = "http://api.zippopotam.us/us/{}/{}".format(state, city)
    json_response = requests.get(api).json()
    lng = json_response['places'][0]['longitude']
    lat = json_response['places'][0]['latitude']
    return lat, lng

def find_lnglat_by_code():
    code = request.form['code']

    conn = get_db_connection()
    statement = statement = """SELECT  latitude, longitude  FROM schools
                    WHERE url_code == '{}' """.format(code)
    row = conn.execute(statement)
    row = row.fetchone()
    lat, lng = list(row)[0], list(row)[1]
    return lat,lng


#--------------------------------
app.run(debug = True)

