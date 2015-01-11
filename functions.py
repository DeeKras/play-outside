import requests
import pygeoip
from flask import redirect, url_for, flash, request

from forms import SearchForm, SchoolForm
from models import SchoolData, SchoolWeather
from config import  db

geoip_data = pygeoip.GeoIP('/home/deekras/PythonEnv/My work/Playoutside/GeoLiteCity.dat')


       


def verify_input(form):
    print 'start verify'
    error=""
    if form.search_by.data not in ['postal', 'place', 'code']:
        error = 'You must click one of the radio buttons'
    elif form.search_by.data == 'postal' and form.postal.data == "":
        error = 'You selected POSTAL but you did not include a postal code. Please enter a postal code.'
    elif form.search_by.data == 'place' and \
            (form.country.data == "" or form.state.data == "" or form.city.data == ""):
        error = 'You selected PLACE but you did not include either a country, state or city. Please enter all 3.'
    elif form.search_by.data == 'code' and form.code.data == "":
        error = 'You selected CODE but you did not include your code. Please enter it.'
    print 'error: ' + error
    print 'end verify'
    return error

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
    print 'in postal'
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
    print error, weather
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
    if school is None:
        
        weather = None
        error = 'The CECE-code is inaccurate. Please try again.'
    else:
        print school
        lat = school.latitude
        lng = school.longitude

        flag = '2'
        filler = school.school_name
        weather = get_weather_info(lat, lng), flag, filler
        error = None
    return weather, error






