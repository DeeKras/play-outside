from os import urandom
from random import randrange
import requests
import time
import math
import datetime
from string import capwords

from config import db

forecast_io_key = 'fc0baa44318f233c63d149ae0fea7c85'
api_forecast_io = 'https://api.forecast.io/forecast/{}/{},{},{}'
api_googlemaps = 'http://maps.googleapis.com/maps/api/geocode/json?address={}'


class Search(db.Model):
    timestamp = db.Column(db.DateTime, primary_key=True)
    search_by = db.Column(db.String)
    postal = db.Column(db.String)
    country = db.Column(db.String)
    state = db.Column(db.String)
    city = db.Column(db.String)
    user_name = db.Column(db.String)

    def __init__(self, timestamp, search_by, postal, country, state, city, user_name):
        self.timestamp = timestamp
        self.search_by = search_by
        self.postal = postal
        self.country = country
        self.state = state
        self.city = city
        self.user_name = user_name

class SchoolData(db.Model):
    user_name = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, nullable=False)
    school_name = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)
    postal = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    longitude = db.Column(db.String) 
    latitude = db.Column(db.String) 
    cellphone = db.Column(db.String, nullable=False)
    send_email = db.Column(db.Boolean, default=True)
    send_text = db.Column(db.Boolean, default=True)

    def __init__(self, user_name, email, school_name, first_name, last_name, 
                    city, state, postal, country, cellphone, send_email, send_text):
        self.user_name = user_name
        self.email = email
        self.school_name = school_name.title()
        self.first_name = first_name.title()
        self.last_name = last_name.title()
        self.city = city.title()
        self.postal = postal
        self.cellphone = cellphone
        self.send_email = send_email
        self.send_text = send_text
        self.latitude = ''
        self.longitude = ''


        if country.lower() not in ['us', 'usa', 'united states'] and len(country) >4:
            self.country = country.title()
        elif country in ['us', 'usa', 'united states']:
            self.country = "USA"
        elif len(country)< 4:
            self.country = country.upper()
 
        if len(state) == 2:
            self.state = state.upper()
        else:
            self.state = state.title()
    
        if self.country == 'USA' and postal:
            api = "http://api.zippopotam.us/us/{}".format(self.postal)
            json_response = requests.get(api).json()
            self.latitude = json_response['places'][0]['latitude']
            self.longitude = json_response['places'][0]['longitude']
        else:
            search_place = '{},{},{}'.format(self.country, self.state, self.city)
            api = api_googlemaps.format(search_place)
            json_response = requests.get(api).json()
            self.latitude = json_response['results'][0]['geometry']['location']['lat']
            self.longitude = json_response['results'][0]['geometry']['location']['lng']

        
class SchoolWeather(object):
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng
        self.date = '{}T12:00:00-0400'.format(datetime.date.today())
        self.pretty_date = ""

        lookup_url = api_forecast_io.format(forecast_io_key, self.lat, self.lng, self.date)
        print lookup_url
        self.json_response = requests.get(lookup_url).json()

        self.weather_data = self.json_response[u'hourly'][u'data']
        self.hourly = self.create_weatherdetails_dict()

    # def __call__(self):  #how to get this to call
       
 
# ----------------
    def find_hour(self, i):
        return self.weather_data[i][u'time']

    def find_icon(self, i):
        icon_type = self.weather_data[i][u'icon']
        return "\static\weather_icons\{}.png".format(weather_icons_dict[icon_type])
        
    def find_precip(self,i):
        if u'precipType' in self.weather_data[i]:
            precipType = self.weather_data[i][u'precipType']
            precipProbability = '{}%'.format(self.weather_data[i][u'precipProbability'])
            precipIntensity = self.weather_data[i][u'precipIntensity']
        else:
            precipType = 'N/A'
            precipProbability = 'N/A'
            precipIntensity = 'N/A'

        return precipType, precipProbability, precipIntensity

    def find_temperature(self,i):
        _tempF = self.weather_data[i][u'temperature']
        return _tempF

    def find_windspeed(self,i):
        return self.weather_data[i][u'windSpeed']

    def calculate_windchill(self, windspeed, temperature):
        V = windspeed
        T = temperature
        return  math.ceil(35.74 + (0.6215*T) - (35.75*(V**0.16)) + (0.4275*T*(V**0.16)))

#---------------------
    def set_pretty_date(self,date):
        _dd = date.split('T')[0].split('-')
        self.pretty_date =  '{}/{}/{}'.format(_dd[1], _dd[2], _dd[0])

    def pretty_hour(self,_time):
        print _time
        _time_tup = convert_unixtime_time(_time).split(' ')
        print _time_tup
        return '{} {}'.format(_time_tup[1], _time_tup[2])

    def pretty_temperatures(self,_tempF):
        _tempC = convert_to_celsius(_tempF)
        return '{:<20}F / {:>20} C'.format(_tempF, _tempC)

    def pretty_windspeed(self, _windspeed):
        return '{} mph'.format(_windspeed)

    def pretty_windchill(self, _windchillF):
        _windchillC = convert_to_celsius(_windchillF)
        return '{:<20}F / {:>20} C'.format(_windchillF, _windchillC)

    def should_play_outside(self, windchill):
        if windchill>=32:
            playability = 'green'
        elif windchill>=13:
            playability = 'yellow'
        else:
            playability = 'red'
        return playability

    #---------------
    def create_weatherdetails_dict(self):
        # this should create a dictionaty of the pretty data - to be passed to html. 
        #this can be in the views module
        self.set_pretty_date(self.date)

        gmt_offset = self.json_response[u'offset']
        start_point = 9 - gmt_offset
        end_point = start_point + 8

        hourly = []

        for i in range(start_point, end_point):
            windchill = self.calculate_windchill(self.find_windspeed(i), self.find_temperature(i))
            
            hour = {
                    'time' : self.weather_data[i][u'time'],
                    'hour': self.pretty_hour(self.find_hour(i)),
                    'icon': self.weather_data[i][u'icon'],
                    'icon_png': self.find_icon(i),
                    'temperature': self.pretty_temperatures(self.find_temperature(i)),
                    'windspeed': self.pretty_windspeed(self.find_windspeed(i)),
                    'precipType': self.find_precip(i)[0],
                    'precipProbability': self.find_precip(i)[1],
                    'precipIntensity': self.find_precip(i)[2],
                    'windchill': self.pretty_windchill(windchill),
                    'playability': self.should_play_outside(windchill)
                    }
            hourly.append(hour)
        print hourly
        return hourly


#-----------------------       



def convert_unixtime_time(unix_time):
    return time.strftime("%D %I:%M %p", time.gmtime(int(unix_time)))

def convert_to_celsius(tempF):
    return round((int(tempF) -  32)*.55)


weather_icons_dict = {
            'clear-day': 'sunny',
            'clear-night': 'sunny_night',
            'rain': 'shower3',
            'snow': 'snow4',
            'sleet':'sleet' ,
            'wind': 'wind', 
            'fog': 'fog',
            'cloudy':'cloudy5',
            'partly-cloudy-day':'cloudy2',
            'partly-cloudy-night':'cloudy2_night',
            'hail':'hail', 
            'thunderstorm':'tstorm3',
            'tornado': 'tornado',}