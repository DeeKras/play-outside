import requests
import pygeoip
from flask import redirect, url_for, flash, request

from forms import SearchForm, SchoolForm
from models import SchoolData, SchoolWeather
from config import  db

ipinfo_key = '607dd31739e77a661a0152941384503e0d190bd9166a89ff2cd130cc4121ede4'

# geoip_data = pygeoip.GeoIP('/home/deekras/PythonEnv/My work/Playoutside/GeoLiteCity.dat')
api_googlemaps = 'http://maps.googleapis.com/maps/api/geocode/json?address={}'
ipinfo_api = 'http://api.ipinfodb.com/v3/ip-city/?key={}&ip={}&format=json'
# http://api.ipinfodb.com/v3/ip-city/?key=<your_api_key>&ip=74.125.45.100&format=json



       


def verify_input(form):
    if form.submit_user.data and form.user_name.data == "":
        return 'You selected YOUR ACCOUNT but you did not include your user name. Please enter it.'
    elif form.submit_zip.data and form.zipcode.data == "":
        return 'You selected ZIP but you did not include a zip code. Please enter a US ZIP CODE.'
    elif form.submit_place.data and form.country.data == "":
        return 'You selected PLACE but you did not include a country. Please enter a COUNTRY.'
    elif form.submit_place.data and form.city.data == "":
        return 'You selected PLACE but you did not include a city. Please enter a CITY.'
    elif form.submit_place.data and form.country.data.lower() in ['us', 'usa', 'united states'] and form.state.data =="":
        return 'You entered US as country, you must also submit STATE and CITY.'
    return None

def get_weather(form, request):
    if form.submit_zip.data:
        weather, error = weather_by_zip(form.zipcode.data)
    elif form.submit_place.data:
        weather, error = weather_by_place(form.country.data, form.state.data, form.city.data)
    elif form.submit_user.data:                                            
        weather, error = weather_by_user(form.user_name.data)
    else:
        weather, error = weather_by_ip(request)
    return weather, error

def get_weather_info(lat, lng):
    weather_for_city = SchoolWeather(lat, lng)
    hourly = weather_for_city.hourly
    display_date = weather_for_city.pretty_date
    return hourly, display_date

def weather_by_ip(request):
    if request.headers.getlist("X-Forwarded-For"):
       ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
       ip = request.remote_addr

    ip_data = requests.get(ipinfo_api.format(ipinfo_key, ip)).json()
    lat = ip_data['latitude']
    lng = ip_data['longitude']
    city = ip_data['cityName']
    region = ip_data['regionName']
    country = ip_data['countryName']

    flag = '0'
    filler = '{}, {} {}'.format(city, region, country)
    place = filler
    weather = get_weather_info(lat, lng), flag, filler, place
    error = None
    return weather, error

def weather_by_zip(zipcode):
    api = "http://api.zippopotam.us/us/{}".format(zipcode)
    json_response = requests.get(api).json()
    if json_response == {}:
        weather = None
        error = 'The zip code you entered is not valid. Please reenter.'
    else:
        place_details = json_response['places'][0]
        lat = place_details['latitude']
        lng = place_details['longitude']
        place = '{}, {} US'.format(place_details['place name'], place_details['state abbreviation'])
        
        flag = '1'
        filler = zipcode
        weather = get_weather_info(lat, lng), flag, filler, place
        error = None
    return weather, error

def weather_by_place(country, state, city):
    if state:
        search_place = filler = '{},{},{}'.format(country, state, city)
    else:
        search_place = filler = '{},{}'.format(country, city)
    
    api = api_googlemaps.format(search_place)
    json_response = requests.get(api).json()
    if json_response[u'status'] == u'ZERO_RESULTS':
        weather = None
        error = 'The data you entered in not accurate. Please reenter.'
    else:
        lat = json_response['results'][0]['geometry']['location']['lat']
        lng = json_response['results'][0]['geometry']['location']['lng']

        place = pretty_place(country, state, city)
        flag = '1'
        weather = get_weather_info(lat, lng), flag, filler, place
        error = None
    return weather, error

def weather_by_user(user_name):
    school = db.session.query(SchoolData).filter_by(user_name=user_name).first()
    if school is None:
        weather = None
        error = 'The user name is inaccurate. Please try again.'
    else:
        lat = school.latitude
        lng = school.longitude

        flag = '2'
        filler = school.school_name
        place = '{}, {} {}'.format(school.city, school.state, school.country)
        weather = get_weather_info(lat, lng), flag, filler, place
        error = None
    return weather, error

def pretty_place(country, state, city):
    city = city.title()
    if state:
        if country.lower() in ['us', 'usa', 'united states']:
            country = "USA"
            if len(state) == 2:
                state = state.upper()
            else:
                state = state.title()
            return '{}, {} {}'.format(city, state, country)
        else:
            return '{}, {} {}'.format(city, state, country.title())
    else:
        return '{}, {}'.format(city, country.title())
    

    
