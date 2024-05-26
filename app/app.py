from flask import Flask, render_template, url_for, flash, redirect, request
from app.forms.forms import LoginForm, createAccount
from app.models import db, User, Location
import requests
from geopy.geocoders import Nominatim
app=Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)
API_KEY = 'GWYm9XH0pw9IN0pk72zylGTmSZ7b1LBX'  # Replace with your actual API key
#Secret key is required for the login form.
with app.app_context():
    db.create_all()

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/get_weather', methods=['POST'])
def get_weather_route():
    location = request.form['location']
    weather = get_weather(location)
    if weather:
        return render_template('home.html', weather=weather, error=None)
    else:
        return render_template('index.html', weather=None, error="Location not found or weather data not available")

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
                }
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None


if __name__ == '__main__':
    app.run(debug=True)








