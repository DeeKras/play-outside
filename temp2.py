from flask import Flask, render_template, request, redirect, session, make_response
import requests
import pygeoip
import arrow
import datetime

rawdata = pygeoip.GeoIP('/home/deekras/PythonEnv/My work/Playoutside/GeoLiteCity.dat')

forecast_io_key = 'fc0baa44318f233c63d149ae0fea7c85'
api_forecast_io = 'https://api.forecast.io/forecast/{}/{},{},{}'


app = Flask(__name__)
db = '/home/deekras/PythonEnv/PlayOutside/schools.db'



date = '{}T12:00:00-0400'.format(str(datetime.date.today()))

def get_db_connection():
    conn = sqlite3.connect(db)
    conn.text_factory = str
    return conn

@app.route('/')
def find_lnglat_by_ip():
    ip = request.remote_addr
    if '127.0.0.1' == ip:
        ip = requests.get("http://icanhazip.com/").content
        data = rawdata.record_by_name(ip)

        lat = data['latitude']
        lng = data['longitude']
    
    return lat, lng

def find_lnglat_by_postal():
	postal = request.form[postal]
	api = "http://api.zippopotam.us/us/{}".format(postal)
	json_response = requests.get(api).json()
    lng = json_response['places'][0]['longitude']
    lat = json_response['places'][0]['latitude']
   
    return lat, lng

def find_lnglat_by_place():
	state = request.form[state]
	city = request.form[postal]
	api = "http://api.zippopotam.us/us/{}/{}".format(state, city)
	json_response = requests.get(api).json()
    lng = json_response['places'][0]['longitude']
    lat = json_response['places'][0]['latitude']

    return lat, lng

def find_lnglat_by_code():
    code = request.form['code']
    conn = get_db_connection()
    statement = """SELECT  latitude as lat, longitude as lng, FROM schools
                    WHERE url_code == '{}'""".format(code)
    row = conn.execute(statement)
    row = row.fetchone()

    return lat, lng



lookup_url = api_forecast_io.format(forecast_io_key, lat, lng, date)
json_response = requests.get(lookup_url).json()


app.run(debug = True)