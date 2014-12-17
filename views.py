from flask import Flask, render_template,request, flash, redirect, url_for
from flask.ext.sqlalchemy import SQLAlchemy
import requests
import datetime
import pygeoip
import sqlite3
from os import urandom

from models import SchoolWeather
from forms import SearchForm


app = Flask(__name__)
app.secret_key = urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://SchoolWeather.db'
db = SQLAlchemy(app)
rawdata = pygeoip.GeoIP('/home/deekras/PythonEnv/My work/Playoutside/GeoLiteCity.dat')

# db_codes = '/home/deekras/PythonEnv/PlayOutside/schools.db' # need to move the data from here to other db

def get_db_connection():
    conn = sqlite3.connect(db)
    conn.text_factory = str
    return conn

@app.route('/weather', methods = ['GET','POST'])
def weather():
    form = SearchForm()
    if request.method == 'POST':

        if form.search_by.data not in ['postal', 'place', 'code']:
            print '1'
            flash('You must click one of the radio buttons')
            return render_template('search.html', form=SearchForm())
        
        if form.search_by.data == 'postal':
            return postal()

        
        elif form.search_by.data == 'place':
            if form.country.data and form.state.data and form.city.data:
                lat, lng = find_lnglat_by_place()
            else:
                flash ('You selected PLACE but you did not include either a country, state or city. Please enter all 3.')
                return redirect(url_for('search'))
        
        elif form.search_by.data == 'code':
            print '------------------------{}'.format(request.form['code'])
            if form.code.data:
                lat, lng = find_lnglat_by_code()
            else: 
                flash ('You selected CODE but you did not include your code. Please enter it.')
                return redirect(url_for('search'))
    
    elif request.method == 'GET':
        lat, lng = find_lnglat_by_ip()
        return get_weather(lat, lng)
        

        

 
@app.route('/search',  methods=['GET','POST'])   
def search():
    return render_template('search.html', form=SearchForm())

#------------- error trapping ----------

def get_weather(lat, lng):
    weather_for_city = SchoolWeather(lat, lng)
    hourly =  weather_for_city.hourly
    display_date = weather_for_city.pretty_date
    place = '{}, {} {}'.format(weather_for_city.city, weather_for_city.state, weather_for_city.country)

    return render_template('weather.html', 
                        place=place,
                        display_date=display_date, 
                        hourly=hourly)

def postal():
    form = SearchForm()
    if form.postal.data == "":
        flash('You selected POSTAL but you did not include a postal code. Please enter a postal code.')
        return redirect(url_for('search'))
    elif form.postal.data != "":
        api = "http://api.zippopotam.us/us/{}".format(form.postal.data)
        json_response = requests.get(api).json()
        if json_response == {}:
            flash ('The postal code you selected is not valid. Please check the number and try again.')
            return redirect(url_for('search'))
        else:
            print "**********"
            lng = json_response['places'][0]['longitude']
            lat = json_response['places'][0]['latitude']
            return get_weather(lat, lng)

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



