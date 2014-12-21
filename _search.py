from flask import Flask, render_template, request
import requests
import pygeoip
import datetime
import sqlite3

rawdata = pygeoip.GeoIP('/home/deekras/PythonEnv/My work/Playoutside/GeoLiteCity.dat')
db = '/home/deekras/PythonEnv/PlayOutside/schools.db'

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect(db)
    conn.text_factory = str
    return conn

@app.route('/weather')
def find_lnglat_by_search():
    if request.form[searchby] == 'postal':
        find_lnglat_by_postal()
    elif request.form[searchby] == 'place':
        find_lnglat_by_place()
    elif request.form[searchby] == 'code':
        find_lnglat_by_code()
    else:
        find_lnglat_by_ip()
    return lat, lng

def find_lnglat_by_ip():
    ip = request.remote_addr
    if '127.0.0.1' == ip:
        ip = requests.get("http://icanhazip.com/").content
        data = rawdata.record_by_name(ip)

        lat = data['latitude']
        lng = data['longitude']
    return lat, lng

def find_lnglat_by_postal():
    zipcode = request.form[postal]

    api = "http://api.zippopotam.us/us/{}".format(zipcode)
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

app.run(debug = True)