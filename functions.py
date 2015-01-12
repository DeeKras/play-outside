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
    if form.submit_code.data and form.code.data == "":
        return 'You selected CODE but you did not include your code. Please enter it.'
    elif form.submit_zip.data and form.zipcode.data == "":
        return 'You selected ZIP but you did not include a zip code. Please enter a US ZIP CODE.'
    elif form.submit_place.data and form.country.data == "":
        return 'You selected PLACE but you did not include a country. Please enter a COUNTRY.'
    elif form.submit_place.data and form.city.data == "":
        return 'You selected PLACE but you did not include a city. Please enter a CITY.'
    elif form.submit_place.data and form.country.data.lower() in ['us', 'usa', 'united states'] and form.state.data =="":
        return 'You entered US as country, you must also submit STATE and CITY.'
    return None

def get_weather(form):
    if form.submit_zip.data:
        weather, error = weather_by_zip(form.zipcode.data)
    elif form.submit_place.data:
        weather, error = weather_by_place(form.country.data, form.state.data, form.city.data)
    elif form.submit_code.data:                                            
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

def weather_by_zip(zipcode):
    api = "http://api.zippopotam.us/us/{}".format(zipcode)
    json_response = requests.get(api).json()
    if json_response == {}:
        weather = None
        error = 'The zip code you entered is not valid. Please reenter.'
    else:
        lat = json_response['places'][0]['latitude']
        lng = json_response['places'][0]['longitude']
        
        flag = '1'
        filler = zipcode
        weather = get_weather_info(lat, lng), flag, filler
        error = None
    return weather, error

def weather_by_place(country, state, city):
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

