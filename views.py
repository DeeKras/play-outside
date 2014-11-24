from flask import Flask, render_template,request, flash
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
app.secret_key = 'some_secret'


@app.route('/weather', methods = ['GET','POST'])
def display_weather():
    print request.method
    if request.method == 'GET':
        print 'x'
        lat, lng = find_lnglat_by_ip()

    elif request.method == 'POST':

        if not request.form.has_key('searchby'):
            flash('You must click one of the radio buttons')
            return render_template('search.html')
        
        if request.form['searchby'] == 'postal':
            lat, lng = find_lnglat_by_postal()

        
        elif request.form['searchby'] == 'place':
            if request.form['country'] != '' and request.form['state'] != '' and request.form['city'] != '':
                lat, lng = find_lnglat_by_place()
            else:
                flash ('You selected PLACE but you did not include either a country, state or city. Please enter all 3.')
                return render_template('search.html')
        
        elif request.form['searchby'] == 'code':
            print '------------------------{}'.format(request.form['code'])
            if request.form['code'] != '':
                lat, lng = find_lnglat_by_code()
            else: 
                flash ('You selected CODE but you did not include your code. Please enter it.')
                return render_template('search.html')
    
    date = '{}T12:00:00-0400'.format(datetime.date.today())
    weather_for_city = SchoolWeather(lat, lng, date)
    print weather_for_city.city

    hourly =  weather_for_city.hourly
    print weather_for_city.hourly
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

#------------- error trapping ----------
def postal(postal):
    if postal =='':
        flash ('You selected POSTAL but you did not include a postal code. Please enter a postal code.')
        return render_template('search.html')
    elif postal != '':
        zipcode = request.form['postal']
        api = "http://api.zippopotam.us/us/{}".format(zipcode)
        json_response = requests.get(api).json()
        if json_response == {}:
            flash ('The postal code you selected is not valid. Please check the number and try again.')
            return render_template('search.html')
        else:
            lng = json_response['places'][0]['longitude']
            lat = json_response['places'][0]['latitude']
            return lat, lng







 





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
    city = request.form['city']

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

