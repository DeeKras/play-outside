from flask import Flask, render_template,request, flash, redirect,  session, url_for
from flask.ext.sqlalchemy import SQLAlchemy
# from flaskext.mail import  Message
import pygeoip

from forms import SearchForm, SchoolForm
from models import SchoolData, SchoolWeather
from config import app, db

from functions import get_weather, verify_input, get_weather_info, weather_by_user


# geoip_data = pygeoip.GeoIP('/home/deekras/PythonEnv/My work/Playoutside/GeoLiteCity.dat')


# db.create_all()
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
    return display_weather(form, request)

@app.route('/weather/<user_name>', methods=['GET'])
def display_specific_school(user_name):
    print user_name
    weather, error = weather_by_user(user_name)
    (hourly, display_date), flag, filler, place  = weather
    return render_template("weather.html", hourly=hourly,
                                        display_date=display_date,
                                        filler=filler,
                                        place=place,
                                        flag=flag)

@app.route('/search',  methods=['GET', 'POST'])   
def search():
    return render_template('search.html', form=SearchForm())


@app.route('/school_info', methods=['GET', 'POST'])
def school_info():
    if request.method =='POST':
        form = SchoolForm()
        school = SchoolData(form.user_name.data,
                            form.email.data,
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

        # msg = Message("Welcome to weather watch",  
        #           sender="dee@deekras2.com",  
        #           recipients=[SchoolData(school.email)])
        # mail.send(msg)

        place = '{}, {} {}'.format(school.city, school.state, school.country)
        hourly, display_date = get_weather_info(school.latitude, school.longitude)
        return render_template("weather.html", hourly=hourly,
                                            display_date=display_date,
                                            filler=form.school_name.data,
                                            place=place,
                                            flag='2')    

    if request.method == 'GET':
        return render_template('schoolform.html', form=SchoolForm())


def display_weather(form, request):
    weather, error = get_weather(form, request)
    if error:
        flash(error)
        return redirect(url_for('search'))  # need to figure out how to leave the inputed data in the 
                                            # in the search form when it is rendered. is that javascript?
    else:
        (hourly, display_date), flag, filler, place  = weather
        return render_template("weather.html", hourly=hourly,
                                        display_date=display_date,
                                        filler=filler,
                                        place=place,
                                        flag=flag)