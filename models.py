from os import urandom
from random import randrange
import requests
import time
import math
import datetime

from functions import find_by_postal
from config import db

forecast_io_key = 'fc0baa44318f233c63d149ae0fea7c85'
api_forecast_io = 'https://api.forecast.io/forecast/{}/{},{},{}'
api_googlemaps = 'http://maps.googleapis.com/maps/api/geocode/json?latlng={},{}&sensor=true'




class Search(db.Model):
    timestamp = db.Column(db.DateTime, primary_key=True)
    search_by = db.Column(db.String)
    postal = db.Column(db.String)
    country = db.Column(db.String)
    state = db.Column(db.String)
    city = db.Column(db.String)
    code = db.Column(db.String)

    def __init__(self, timestamp, search_by, postal, country, state, city, code):
        self.timestamp = timestamp
        self.search_by = search_by
        self.postal = postal
        self.country = country
        self.state = state
        self.city = city
        self.code = code

    def __repr__(self):
        if self.search_by == "postal":
            searched = self.postal
        elif self.search_by == "place":
            searched = "{}: {}, {}".format(self.country, self.state, self.city)
        elif self.search_by == "code":
            searched = self.code
        else:
            searched = 'by IP'

        return 'Searched for : {}'.format(searched)

class SchoolData(db.Model):
    CECE_code = db.Column(db.String, primary_key=True)
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

    def __init__(self, email, school_name, first_name, last_name, 
                    city, state, postal, country, cellphone, send_email, send_text):
        self.CECE_code = str("Z{}".format(randrange(99999,9999999)))
        self.email = email
        self.school_name = school_name
        self.first_name = first_name
        self.last_name = last_name
        self.city = city
        self.state = state
        self.postal = postal
        self.country = country
        self.longitude = find_by_postal(postal)[1]
        self.latitude = find_by_postal(postal)[0]
        self.cellphone = cellphone
        self.send_email = send_email
        self.send_text = send_text

class SchoolWeather(object):
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng
        self.date = '{}T12:00:00-0400'.format(datetime.date.today())
        self.neighborhood = ""
        self.city = ""
        self.state = ""
        self.country = ""
        self.pretty_date = ""

        lookup_url = api_forecast_io.format(forecast_io_key, self.lat, self.lng, self.date)
        self.json_response = requests.get(lookup_url).json()

        self.weather_data = self.json_response[u'hourly'][u'data']
        self.hourly = self.create_weatherdetails_dict()



    # def __call__(self):  #how to get this to call
       


        
    def find_place_from_latlng(self):
        lookup_url = api_googlemaps.format(self.lat, self.lng)
        json_response = requests.get(lookup_url).json()

        address_components = json_response[u'results'][0][u'address_components']
        self.neighborhood = address_components[2][u'long_name']
        self.city =  address_components[3][u'long_name']
        self.state = address_components[5][u'long_name']
        self.country = address_components[6][u'long_name']



 
# ----------------
    def find_hour(self, i):
        return self.weather_data[i][u'time']

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
        _time_tup = convert_unixtime_time(_time).split(' ')
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
        # this should create a dictionaty of the pretty data - to be passed to html. this can be in the views module
        self.find_place_from_latlng()
        self.set_pretty_date(self.date)

        gmt_offset = self.json_response[u'offset']
        start_point = 9 + gmt_offset
        end_point = start_point + 8

        hourly = []

        for i in range(start_point, end_point):
            windchill = self.calculate_windchill(self.find_windspeed(i), self.find_temperature(i))
            
            hour = {
                    'hour': self.pretty_hour(self.find_hour(i)),
                    'temperature': self.pretty_temperatures(self.find_temperature(i)),
                    'windspeed': self.pretty_windspeed(self.find_windspeed(i)),
                    'precipType': self.find_precip(i)[0],
                    'precipProbability': self.find_precip(i)[1],
                    'precipIntensity': self.find_precip(i)[2],
                    'windchill': self.pretty_windchill(windchill),
                    'playability': self.should_play_outside(windchill)
                    }
            hourly.append(hour)
        return hourly


#-----------------------       



def convert_unixtime_time(unix_time):
    return time.strftime("%D %I:%M %p", time.gmtime(int(unix_time)))

def convert_to_celsius(tempF):
    return round((int(tempF) -  32)*.55)

