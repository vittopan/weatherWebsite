from flask import Flask, render_template, url_for, flash, redirect, request, session
from app.forms.forms import LoginForm, createAccount
from app.models import db, User
import requests
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)
API_KEY = 'GWYm9XH0pw9IN0pk72zylGTmSZ7b1LBX'  # Replace with your actual API key

with app.app_context():
    db.create_all()

@app.route('/')
@app.route('/home')
def home():
    user = None
    if 'username' in session:
        user = User.query.get(session['user_id'])
    return render_template('home.html', user=user)

@app.route('/get_weather', methods=['POST'])
def get_weather_route():
    try:
        location = request.form['location']
        daily_weather, hourly_weather, lat, lon = get_weather(location)
        current_date = datetime.now()
        all_dates = [current_date + timedelta(days=i) for i in range(0, 5)]
        
        combined_data = list(zip(all_dates, daily_weather))

        if daily_weather:
            return render_template('home.html', daily_weather=daily_weather, hourly_weather=hourly_weather, today=current_date, combined_data=combined_data, lat=lat, lng=lon, error=None)
        else:
            return render_template('home.html', daily_weather=None, hourly_weather=None, today=current_date, combined_data=[], lat=lat, lng=lon, error="Location not found or weather data not available")
    except Exception as e:
        print("Error:", e)  # Debugging statement
        return render_template('home.html', daily_weather=None, hourly_weather=None, today=datetime.now(), combined_data=[], error="Error processing location")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            session['location'] = user.location
            flash('Login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = createAccount()
    if form.validate_on_submit():
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            flash('Username or email already exists. Please choose another.', 'danger')
        else:
            user = User(username=form.username.data, email=form.email.data, location=form.location.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            print('Form validation failed')
            print(form.errors)
    return render_template('register.html', form=form)

def get_weather(location):
    API_KEY = 'GWYm9XH0pw9IN0pk72zylGTmSZ7b1LBX'  # Replace with your actual API key

    geolocator = Nominatim(user_agent="weather_app")
    location_data = geolocator.geocode(location)

    if location_data:
        lat = location_data.latitude
        lng = location_data.longitude

        # Fetching daily weather data for the next 7 days
        daily_weather_url = f'https://api.tomorrow.io/v4/timelines?apikey={API_KEY}&location={lat},{lng}&fields=temperature,humidity,windSpeed,weatherCode&timesteps=1d&units=metric&timezone=auto'
        daily_response = requests.get(daily_weather_url)
        daily_weather_data = daily_response.json()

        # Fetching hourly weather data for the next 6 hours
        hourly_weather_url = f'https://api.tomorrow.io/v4/timelines?apikey={API_KEY}&location={lat},{lng}&fields=temperature,humidity,windSpeed,weatherCode&timesteps=1h&units=metric&timezone=auto'
        hourly_response = requests.get(hourly_weather_url)
        hourly_weather_data = hourly_response.json()

        daily_weather = []
        hourly_weather = []

        if daily_weather_data.get('data'):
            for interval in daily_weather_data['data']['timelines'][0]['intervals']:
                date = interval['startTime']
                formatted_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z").strftime("%d-%b")
                values = interval['values']
                daily_weather.append({
                    'date': formatted_date,
                    'temperature': values['temperature'],
                    'humidity': values['humidity'],
                    'wind_speed': values['windSpeed'],
                    'weather_code': values['weatherCode']
                })

        if hourly_weather_data.get('data'):
            for interval in hourly_weather_data['data']['timelines'][0]['intervals'][:6]:  # Next 6 hours
                time = interval['startTime']
                formatted_time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S%z").strftime("%H:%M")
                values = interval['values']
                hourly_weather.append({
                    'time': formatted_time,
                    'temperature': values['temperature'],
                    'humidity': values['humidity'],
                    'wind_speed': values['windSpeed'],
                    'weather_code': values['weatherCode']
                })

            return daily_weather, hourly_weather, lat, lng
    else:
        print("Location not found.")
        return None, None, None, None

if __name__ == '__main__':
    app.run(debug=True)
