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







