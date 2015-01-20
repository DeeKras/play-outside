import requests
from models import SchoolData, SchoolWeather
from config import  db

ipinfo_key = '607dd31739e77a661a0152941384503e0d190bd9166a89ff2cd130cc4121ede4'
api_googlemaps = 'http://maps.googleapis.com/maps/api/geocode/json?address={}'
ipinfo_api = 'http://api.ipinfodb.com/v3/ip-city/?key={}&ip={}&format=json'

def verify_input(form):
    '''confirms that data entered is valid for the searches. 
       if not saves error message to be displayed on the form'''
   
    if form.submit_user.data and form.user_name.data == "":
        return 'You selected YOUR ACCOUNT but you did not include your user name. Please enter it.'
    elif form.submit_zip.data and form.zipcode.data == "":
        return 'You selected ZIP but you did not include a zip code. Please enter a US ZIP CODE.'
    elif form.submit_place.data and form.country.data == "":
        return 'You selected PLACE but you did not include a country. Please enter a COUNTRY.'
    elif form.submit_place.data and form.city.data == "":
        return 'You selected PLACE but you did not include a city. Please enter a CITY.'
    elif form.submit_place.data and form.country.data.lower() \
            in ['us', 'usa', 'united states'] \
            and form.state.data == "":
        return 'You entered US as country, you must also submit STATE and CITY.'
   

def get_weather_by_ip(request):
    '''tries to get the lng, lat from the ip. and get the weather from the lng, lat. and then prepares for html'''
   
    if request.headers.getlist("X-Forwarded-For"):
       ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
       ip = requests.get('http://icanhazip.com/').content
    
    ip_data = requests.get(ipinfo_api.format(ipinfo_key, ip)).json()
    lat = ip_data['latitude']
    lng = ip_data['longitude']
    city = ip_data['cityName']
    region = ip_data['regionName']
    country = ip_data['countryName']

    html_flag = '0'
    html_place = html_filler = '{}, {} {}'.format(city, region, country)
    weather = (get_detailed_weather_info(lat, lng), html_flag, html_filler, html_place,)
    error = None  #to use the same function, need to have something for the 'error' variable.
    return weather, error


def get_weather_by_zip(zipcode):
    '''tries to get the lng, lat from the zip. and get the weather from the lng, lat. and then prepares for html'''
    
    api = "http://api.zippopotam.us/us/{}".format(zipcode)
    json_response = requests.get(api).json()
    if json_response != {}:
        place_details = json_response['places'][0]
        lat = place_details['latitude']
        lng = place_details['longitude']
        
        
        html_flag = '1'
        html_place = '{}, {} US'.format(place_details['place name'], place_details['state abbreviation'])
        html_filler = zipcode
        weather = (get_detailed_weather_info(lat, lng), html_flag, html_filler, html_place,)
        error = None
    else:
        weather = None
        error = 'The zip code you entered is not valid. Please reenter.'
    return weather, error


def get_weather_by_place(country, state, city):
    '''tries to get the lng, lat from the place. and get the weather from the lng, lat. and then prepares for html'''
    if state:
        search_place = '{},{},{}'.format(country, state, city)
    else:
        search_place = '{},{}'.format(country, city)
    api = api_googlemaps.format(search_place)
    json_response = requests.get(api).json()
    
    if json_response[u'status'] == 'OK':
        if  json_response['results'][0]['address_components'][0]['types'][0] == "locality":
            lat = json_response['results'][0]['geometry']['location']['lat']
            lng = json_response['results'][0]['geometry']['location']['lng']

            html_flag = '1'
            html_place = pretty_place(country, state, city)
            html_filler = search_place
            weather = (get_detailed_weather_info(lat, lng), html_flag, html_filler, html_place,)
            error = None
        else:
            weather = None
            error = 'The data you entered in not accurate. Please reenter.'
    return weather, error


def get_weather_by_user(user_name):
    '''tries to get the user_name from the zip. and get the weather from the lng, lat. and then prepares for html.
        * gets the user from 1. user enters it in search page, 2. it is in the url 3. after new school is added, 
        the weather data is obtained by using this function    '''

    school = db.session.query(SchoolData).filter_by(user_name=user_name).first()
    if school != None:
        lat = school.latitude
        lng = school.longitude

        html_flag = '2'
        html_filler = school.school_name
        html_place = '{}, {} {}'.format(school.city, school.state, school.country)
        weather = (get_detailed_weather_info(lat, lng), html_flag, html_filler, html_place,)
        error = None
    else:
        weather = None
        error = 'The user name is inaccurate. Please try again.'
    return weather, error


def get_detailed_weather_info(lat, lng, days=0):
    ''' actually gets the weather data based on the lng, lat. and prepares the weather data for display'''

    weather_for_city = SchoolWeather(lat, lng, days)
    hourly = weather_for_city.hourly
    display_date = weather_for_city.pretty_date
    summary = weather_for_city.daily_summary
    return hourly, display_date, summary


def pretty_place(country, state, city):
    ''' prepares the 'place' for display'''

    #rewrite as if not
    city = city.title()
    country = country.title()
    state = state.title()

    if len(country) <4:
        country = country.upper()

    if country.lower() in ['us', 'usa', 'united states']:
        country = "USA"

    if len(state) == 2:
        state = state.upper()

    if state:        
        return '{}, {} {}'.format(city, state, country)
    else:
        return '{}, {}'.format(city, country)
    
