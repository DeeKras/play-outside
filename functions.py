import requests
import pygeoip
from flask import redirect, url_for, flash, request


geoip_data = pygeoip.GeoIP('/home/deekras/PythonEnv/My work/Playoutside/GeoLiteCity.dat')

def find_by_ip():
    ip = request.remote_addr
    if ip == '127.0.0.1':
        ip = requests.get("http://icanhazip.com/").content
    data = geoip_data.record_by_addr(ip)

    lat = data['latitude']
    lng = data['longitude']
    return lat, lng

def find_by_postal(postal):
    api = "http://api.zippopotam.us/us/{}".format(postal)
    json_response = requests.get(api).json()
    if json_response == {}:
        return redirect(url_for('search'))
    else:
        lat = json_response['places'][0]['latitude']
        lng = json_response['places'][0]['longitude']
        return lat, lng

def find_by_place(state, city):
    api = "http://api.zippopotam.us/us/{}/{}".format(state, city)
    json_response = requests.get(api).json()
    if json_response == {}:
        return redirect(url_for('search'))
    else:
        lat = json_response['places'][0]['latitude']
        lng = json_response['places'][0]['longitude']
        return lat, lng





