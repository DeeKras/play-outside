from flask import Flask, render_template,request, flash, redirect,  session, url_for
from flask.ext.sqlalchemy import SQLAlchemy
import requests

import sqlite3
from os import urandom


from forms import SearchForm, SchoolForm
from models import SchoolData, SchoolWeather
from functions import find_by_ip, find_by_postal, find_by_postal, find_by_place
from config import app, db

db.create_all()
# db.text_factory = str


@app.route('/weather', methods=['GET', 'POST'])
def weather():
    form = SearchForm()
    if request.method == 'POST':
        if form.search_by.data not in ['postal', 'place', 'code']:
            flash('You must click one of the radio buttons')
            return render_template('search.html', form=SearchForm())
        
        if form.search_by.data == 'postal':
            if form.postal.data == "":
                flash('You selected POSTAL but you did not include a postal code. Please enter a postal code.')
                return redirect(url_for('search'))
            else:
                try:
                    lat, lng = find_by_postal(form.postal.data)
                    flag = '1'
                    filler = form.postal.data
                except TypeError:
                   flash('The postal code you selected is not valid. Please check the number and try again.')
                   return redirect(url_for('search'))

        
        elif form.search_by.data == 'place':
            if form.country.data == "" or form.state.data == "" or form.city.data == "":
                flash('You selected PLACE but you did not include either a country, state or city. Please enter all 3.')
                return redirect(url_for('search'))
            else:
                try:
                    lat, lng = find_by_place(form.state.data, form.city.data)
                    flag = '1'
                    filler = '{}, {}'.format(form.city.data, form.state.data)
                except TypeError:
                    flash('The state or city is inaccurate. Please try again.')
                    return redirect(url_for('search'))
        
        elif form.search_by.data == 'code':  #need to add codes to the db
            if form.code.data == "":
                flash('You selected CODE but you did not include your code. Please enter it.')
                return redirect(url_for('search'))
            else:
                lat, lng, school = find_by_code(form.code.data )
                flag = '2'
                filler = school
    else:
        ip = request.remote_addr
        lat, lng = find_by_ip(ip)
        flag = '0'
        filler = ""

    hourly, display_date, place = get_weather(lat, lng)
    return render_template("weather.html", hourly=hourly,
                                            display_date=display_date,
                                            place=place,
                                            filler=filler,
                                            flag=flag)

   
@app.route('/search',  methods=['GET', 'POST'])   
def search():
    return render_template('search.html', form=SearchForm())


@app.route('/school_info', methods=['GET', 'POST'])
def school_info():
    print request.method
    if request.method =='POST':
        form = SchoolForm()
        school = SchoolData(form.email.data,
                            form.school_name.data,
                            form.first_name.data,
                            form.last_name.data,
                            form.city.data,
                            form.state.data,
                            form.postal.data,
                            form.country.data,
                            form.cellphone.data,
                            form.send_email.data,
                            form.send_text.data,
                            )
        db.session.add(school)
        db.session.commit()
        flag = '2'
        filler = form.school_name.data
        hourly, display_date, place = get_weather(school.latitude, school.longitude)
        return render_template("weather.html", hourly=hourly,
                                            display_date=display_date,
                                            place=place,
                                            filler=filler,
                                            flag=flag)

    if request.method == 'GET':
        return render_template('schoolform.html', form=SchoolForm())


def get_weather(lat, lng):
    weather_for_city = SchoolWeather(lat, lng)
    hourly = weather_for_city.hourly
    display_date = weather_for_city.pretty_date
    place = '{}, {} {}'.format(weather_for_city.city, weather_for_city.state, weather_for_city.country)
    return hourly, display_date, place
    

def find_by_code(code):
    school = db.session.query(SchoolData).filter_by(CECE_code=code).first()
    lat = school.latitude
    lng = school.longitude
    school = school.school_name
    return lat, lng, school


