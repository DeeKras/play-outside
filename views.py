from flask import Flask, render_template,request, flash, redirect,  session, url_for
from flask.ext.sqlalchemy import SQLAlchemy
# from flaskext.mail import  Message
import pygeoip

from forms import SearchForm, SchoolForm
from models import SchoolData, SchoolWeather
from config import app, db
from send_emails import send_new_member_email

from functions import  verify_input, get_detailed_weather_info, get_weather_by_user, \
                        get_weather_by_ip, get_weather_by_place, get_weather_by_zip


@app.route('/', methods=['GET'])
def by_ip():
    weather, error = get_weather_by_ip(request)
    return display_weather(weather, error)


@app.route('/', methods=['POST'])
def by_search():
    form = SearchForm()
    error = verify_input(form)
    if error:
        flash(error)
        return redirect(url_for('search'))  # TODO: need to figure out how to leave the inputed data in the 
    
                                                #       in the search form when it is rendered. is that javascript?
    if form.submit_zip.data:
        weather, error = get_weather_by_zip(form.zipcode.data)
    elif form.submit_place.data:
        weather, error = get_weather_by_place(form.country.data, form.state.data, form.city.data)
    elif form.submit_user.data:                                            
        weather, error = get_weather_by_user(form.user_name.data)


    return display_weather(weather, error)


@app.route('/weather/<user_name>', methods=['GET', 'POST'])
def specific_school(user_name):
    weather, error = get_weather_by_user(user_name)
    return display_weather(weather, error)


@app.route('/school_info', methods=['GET', 'POST'])
def add_new_school():
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

        send_new_member_email(form.email.data, form.user_name.data)

        weather, error = get_weather_by_user(form.user_name.data)
        return display_weather(weather, error)

    if request.method == 'GET':
        return render_template('schoolform.html', form=SchoolForm())


def display_weather(weather, error):
    if error:
        flash(error)
        return redirect(url_for('search'))  # need to figure out how to leave the inputed data in the 
                                            # in the search form when it is rendered. is that javascript?
    else:
        (hourly, display_date, summary), html_flag, html_filler, html_place  = weather
        return render_template("weather.html", hourly=hourly,
                                        summary=summary,
                                        display_date=display_date,
                                        html_filler=html_filler,
                                        html_place=html_place,
                                        html_flag=html_flag)


@app.route('/search',  methods=['GET', 'POST'])   
def search():
    return render_template('search.html', form=SearchForm())