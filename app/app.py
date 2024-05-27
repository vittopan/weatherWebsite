from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from app.forms.forms import LoginForm, createAccount
from app.models import db, User, Location
import requests
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
# Get current date
#date = datetime.now()
#Below is how to get the next dates.
# tomorrow_date = current_date + timedelta(days=1) 
# Format date and month as "Month Day" This is what goes in the HTML
# formatted_date = current_date.strftime("%B %d") 

app=Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)
API_KEY = 'GWYm9XH0pw9IN0pk72zylGTmSZ7b1LBX'  # Replace with your actual API key
#Secret key is required for the login form.
with app.app_context():
    db.create_all()

# Routes to the home page endpoint.
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

#routes to the get_weather page
@app.route('/get_weather', methods=['POST'])
def get_weather_route():
    try:
        location = request.form['location']
        weather, lat, lon = get_weather(location)
        current_date = datetime.now()
        all_dates = [current_date + timedelta(days=i) for i in range(0, 5)]

        if weather:
            # Pass weather, today, and dates variables to the template
            return render_template('home.html', weather=weather, today=current_date, dates=all_dates, lat=lat, lng=lon, error=None)
        else:
            return render_template('home.html', weather=None, today=current_date, dates=all_dates, lat=lat, lng=lon, error="Location not found or weather data not available")
    except Exception as e:
        print("Error:", e)  # Debugging statement
        return render_template('home.html', weather=None, today=datetime.now(), dates=[], error="Error processing location")

# Routes to the login page.
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            flash('Login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

# Routes to the register page.
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = createAccount()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, location=form.location.data)
        user.set_password(form.password.data)
        db.session.add(user) #adds user to db
        db.session.commit() #commits those changes
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

#This is the helper method used to get all the data and put it into JSON
def get_weather(location):
    geolocator = Nominatim(user_agent="weather_app")
    try:
        location_data = geolocator.geocode(location)
        if location_data:
            lat = location_data.latitude
            lng = location_data.longitude

            weather_url = f'https://api.tomorrow.io/v4/timelines?apikey={API_KEY}&location={lat},{lng}&fields=temperature,humidity,windSpeed,weatherCode&timesteps=current&units=metric&timezone=auto'
            response = requests.get(weather_url)
            weather_data = response.json()
            if weather_data.get('data'):
                current_weather = weather_data['data']['timelines'][0]['intervals'][0]['values']
                temperature = current_weather['temperature']
                humidity = current_weather['humidity']
                wind_speed = current_weather['windSpeed']
                weather_code = current_weather['weatherCode']

                return {
                    "address": location_data.address,
                    "temperature": temperature,
                    "humidity": humidity,
                    "wind_speed": wind_speed,
                    "weather_code": weather_code
                }, lat, lng
            else:
                return None, None, None
        else:
            return None, None, None
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None, None, None


if __name__ == '__main__':
    
    app.run(debug=True)








