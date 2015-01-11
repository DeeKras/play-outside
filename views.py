from flask import Flask, render_template,request, flash, redirect,  session, url_for
from flask.ext.sqlalchemy import SQLAlchemy
import requests
import pygeoip
import sqlite3
from os import urandom


from forms import SearchForm, SchoolForm
from models import SchoolData, SchoolWeather
from config import app, db
from functions import get_weather, verify_input, get_weather_info


geoip_data = pygeoip.GeoIP('/home/deekras/PythonEnv/My work/Playoutside/GeoLiteCity.dat')


db.create_all()
# db.text_factory = str


@app.route('/weather', methods=['GET','POST'])
def try_display_weather():
    form = SearchForm()
    if request.method == 'POST':
        error = verify_input(form)
        if error:
            flash(error)
            return redirect(url_for('search'))  # need to figure out how to leave the inputed data in the 
                                                # in the search form when it is rendered. is that javascript?
    return display_weather(form)

def display_weather(form):
    weather, error = get_weather(form)
    if error:
        flash(error)
        return redirect(url_for('search'))  # need to figure out how to leave the inputed data in the 
                                            # in the search form when it is rendered. is that javascript?
    else:
        (hourly, display_date, place), flag, filler = weather
        print place, filler
        return render_template("weather.html", hourly=hourly,
                                        display_date=display_date,
                                        place=place,
                                        filler=filler,
                                        flag=flag)

  
@app.route('/search',  methods=['GET', 'POST'])   
def search():
    print 'search'
    print request.method
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

        hourly, display_date, place = get_weather_info(school.latitude, school.longitude)
        return render_template("weather.html", hourly=hourly,
                                            display_date=display_date,
                                            place=place,
                                            filler=form.school_name.data,
                                            flag='2')    

    if request.method == 'GET':
        return render_template('schoolform.html', form=SchoolForm())


