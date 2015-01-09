from flask import Flask, render_template,request, flash, redirect,  session, url_for
from flask.ext.sqlalchemy import SQLAlchemy
import requests
import pygeoip
import sqlite3
from os import urandom


from forms import SearchForm, SchoolForm
from models import SchoolData, SchoolWeather
from config import app, db


geoip_data = pygeoip.GeoIP('/home/deekras/PythonEnv/My work/Playoutside/GeoLiteCity.dat')


db.create_all()
# db.text_factory = str


@app.route('/weather', methods=['GET','POST'])
def display_weather_post():
    form = SearchForm()
    if request.method == 'POST':
        verify_input(form)

    weather, error = get_weather(form)
    if error:
        flash(error)
        return redirect(url_for('search'))  # need to figure out how to leave the inputed data in the 
                                            # in the search form when it is rendered. is that javascript?
    else:
        (hourly, display_date, place), flag, filler = weather
        return render_template("weather.html", hourly=hourly,
                                            display_date=display_date,
                                            place=place,
                                            filler=filler,
                                            flag=flag)


def verify_input(form):
    if form.search_by.data not in ['postal', 'place', 'code']:
        error = 'You must click one of the radio buttons'
    elif form.search_by.data == 'postal' and form.postal.data == "":
        error = 'You selected POSTAL but you did not include a postal code. Please enter a postal code.'
    elif form.search_by.data == 'place' and \
            (form.country.data == "" or form.state.data == "" or form.city.data == ""):
        error = 'You selected PLACE but you did not include either a country, state or city. Please enter all 3.'
    elif form.search_by.data == 'code' and form.code.data == "":
        error = 'You selected CODE but you did not include your code. Please enter it.'
    if error:
        flash(error)
        return redirect(url_for('search'))  # need to figure out how to leave the inputed data in the 
                                            # in the search form when it is rendered. is that javascript?

def get_weather(form):
    if form.search_by.data == 'postal':
        weather, error = weather_by_postal(form.postal.data)
    elif form.search_by.data == 'place':
        weather, error = weather_by_place(form.country.data, form.state.data, form.city.data)
    elif form.search_by.data == 'code':                                            
        weather, error = weather_by_code(form.code.data)
    else:
        weather, error = weather_by_ip()

    return weather, error



          



   
@app.route('/search',  methods=['GET', 'POST'])   
def search():
    print 'search'
    return render_template('search.html', form=SearchForm())


@app.route('/school_info', methods=['GET', 'POST'])
def school_info():
    print request.method
    if request.method =='POST':
        form = SchoolForm()
        school = SchoolData(form.email.data,
                            form.school_name.data,
                            form.first_name.data,
                            form.last_name.data,
                            form.city.data,
                            form.state.data,
                            form.postal.data,
                            form.country.data,
                            form.cellphone.data,
                            form.send_email.data,
                            form.send_text.data,
                            )
        db.session.add(school)
        db.session.commit()
        flag = '2'
        filler = form.school_name.data
        hourly, display_date, place = get_weather_info(school.latitude, school.longitude)
        return render_template("weather.html", hourly=hourly,
                                            display_date=display_date,
                                            place=place,
                                            filler=filler,
                                            flag=flag
                                            )

    if request.method == 'GET':
        return render_template('schoolform.html', form=SchoolForm())


def get_weather_info(lat, lng):
    weather_for_city = SchoolWeather(lat, lng)
    hourly = weather_for_city.hourly
    display_date = weather_for_city.pretty_date
    place = '{}, {} {}'.format(weather_for_city.city, weather_for_city.state, weather_for_city.country)
    return hourly, display_date, place
    

def weather_by_ip():
    ip = request.remote_addr
    if ip == '127.0.0.1':
        ip = requests.get("http://icanhazip.com/").content
    data = geoip_data.record_by_addr(ip)

    lat = data['latitude']
    lng = data['longitude']

    flag = '0'
    filler = ""
    weather = get_weather_info(lat, lng), flag, filler
    error = None
    return weather, error



def weather_by_postal(postal):
    api = "http://api.zippopotam.us/us/{}".format(postal)
    json_response = requests.get(api).json()
    if json_response == {}:
        weather = None
        error = 'The postal code you entered is not valid. Please reenter.'
    else:
        lat = json_response['places'][0]['latitude']
        lng = json_response['places'][0]['longitude']
        
        flag = '1'
        filler = postal
        weather = get_weather_info(lat, lng), flag, filler
        error = None
    return weather, error



def weather_by_place(country, state, city):
    api = "http://api.zippopotam.us/us/{}/{}".format(state, city)
    json_response = requests.get(api).json()
    if json_response == {}:
        weather = None
        error = 'The data you entered in not accurate. Please reenter.'
    else:
        lat = json_response['places'][0]['latitude']
        lng = json_response['places'][0]['longitude']

        flag = '1'
        filler = '{}, {}'.format(city, state)
        weather = get_weather_info(lat, lng), flag, filler
        error = None
    return weather, error
            

def weather_by_code(code):
    school = db.session.query(SchoolData).filter_by(CECE_code=code).first()
    if school == "":
        weather = None
        error = 'The CECE-code is inaccurate. Please try again.'
    else:
        lat = school.latitude
        lng = school.longitude

        flag = '2'
        filler = school.school_name
        weather = get_weather_info(lat, lng), flag, filler
        error = None
    return weather, error
