import requests
import pygeoip
from flask import redirect, url_for, flash, request

from forms import SearchForm, SchoolForm
from models import SchoolData, SchoolWeather
from config import  db

ipinfo_key = '607dd31739e77a661a0152941384503e0d190bd9166a89ff2cd130cc4121ede4'

geoip_data = pygeoip.GeoIP('/home/deekras/PythonEnv/My work/Playoutside/GeoLiteCity.dat')
api_googlemaps = 'http://maps.googleapis.com/maps/api/geocode/json?address={}'
ipinfo_api = 'http://api.ipinfodb.com/v3/ip-city/?key={}&format=json'.format(ipinfo_key)
# http://api.ipinfodb.com/v3/ip-city/?key=<your_api_key>&ip=74.125.45.100&format=json

       


def verify_input(form):
    error=""
    if form.search_by.data not in ['postal', 'place', 'code']:
        error = 'You must click one of the radio buttons'
    elif form.search_by.data == 'postal' and form.postal.data == "":
        error = 'You selected POSTAL but you did not include a postal code. Please enter a postal code.'
    elif form.search_by.data == 'place' and form.country.data == "":
        error = 'You selected PLACE but you did not include a country. Please enter a country.'
    elif form.search_by.data == 'place' and form.city.data == "":
        error = 'You selected PLACE but you did not include a city. Please enter a city.'
    elif form.search_by.data == 'code' and form.code.data == "":
        error = 'You selected CODE but you did not include your code. Please enter it.'
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
    return hourly, display_date

def weather_by_ip():
    # ip = request.remote_addr
    # if ip == '127.0.0.1':
    #     # ip = requests.get("http://icanhazip.com/").content
        
    # data = geoip_data.record_by_addr( ip)

    # lat = data['latitude']
    # lng = data['longitude']
    ip_data = requests.get(ipinfo_api).json()
    lat = ip_data['latitude']
    lng = ip_data['longitude']
    city = ip_data['cityName']
    region = ip_data['regionName']
    country = ip_data['countryName']

    flag = '0'
    filler = '{}, {} {}'.format(city, region, country)
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
    #needs error trapping if country = us and no state provided
    if state:
        search_place = '{},{},{}'.format(country, state, city)
    else:
        search_place = '{},{}'.format(country, city)
    
    api = api_googlemaps.format(search_place)
    json_response = requests.get(api).json()
    if json_response[u'status'] == u'ZERO_RESULTS':
        weather = None
        error = 'The data you entered in not accurate. Please reenter.'
    else:
        lat = json_response['results'][0]['geometry']['location']['lat']
        lng = json_response['results'][0]['geometry']['location']['lng']

        flag = '1'
        filler = search_place
        weather = get_weather_info(lat, lng), flag, filler
        error = None
    return weather, error
            

def weather_by_code(code):
    school = db.session.query(SchoolData).filter_by(CECE_code=code).first()
    if school is None:
        
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






