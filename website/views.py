import requests
from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint
from .models import User, City, Weather
from . import db
web = Blueprint("web", __name__)

@web.route('/')
def index():
    return render_template('index.html')

@web.route('/weather')
def index_get():
    cities = City.query.all()
    wthr = Weather.query.all()
    for item in wthr:
        db.session.delete(item)
    for city in cities:
        r = get_weather_data(city.name)
        weather = Weather(city_id=city.id, city_name=city.name, temperature=r['main']['temp'], description=r['weather'][0]['description'])
        db.session.add(weather)
        db.session.commit()
    page = request.args.get('page', 1, type=int)
    weather_data = Weather.query.paginate(page=page, per_page=10)

    return render_template('weather.html', weather_data=weather_data)

@web.route('/msg', methods=['POST'])
def index_post():
    new_city = request.form.get('city')

    err_msg = ''

    if new_city:
        old_city = City.query.filter_by(name=new_city).first()

        if not old_city:
            r = get_weather_data(new_city)
            if r['cod'] == 200:
                new_city_obj = City(name=new_city)

                db.session.add(new_city_obj)
                db.session.commit()
            else:
                err_msg = 'That city dont exist.'
        else:
            err_msg = 'You tried entering a city that already exists.'

    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('City added successfully!', 'success')

    return redirect(url_for('web.index_get'))

@web.route('/delete/<string:city_id>')
def delete_city(city_id):
    city_id = int(city_id)
    city = City.query.filter_by(id=city_id).first() #this could be .get too
    db.session.delete(city)
    db.session.commit()

    flash(f'Deleted { city.name }', 'success')
    return redirect(url_for('web.index_get'))

def get_weather_data(city):

    url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=imperial&appid=b0ff101d1130a5b8ad84e42abe4b4102'

    r = requests.get(url).json()

    return r
