from flask import Flask, render_template, url_for, flash, redirect, request, session
from app.forms.forms import LoginForm, createAccount  # Importing form classes from another module
from app.models import db, User  # Importing database models
import requests  # Library for making HTTP requests
from geopy.geocoders import Nominatim  # Library for geocoding
from datetime import datetime, timedelta  # Library for handling dates and times

app = Flask(__name__)  # Creating a Flask application instance
app.config['SECRET_KEY'] = 'your_secret_key'  # Secret key for securing session data
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Database URI
db.init_app(app)  # Initializing SQLAlchemy with the Flask app
API_KEY = 'GWYm9XH0pw9IN0pk72zylGTmSZ7b1LBX'  # API key for weather data (replace with actual API key)

with app.app_context():
    db.create_all()  # Creating all database tables defined in models.py

# Route for the home page
@app.route('/')
@app.route('/home')
def home():
    user = None
    if 'username' in session:
        user = User.query.get(session['user_id'])
    return render_template('home.html', user=user)

# Route for getting weather data
@app.route('/get_weather', methods=['POST'])
def get_weather_route():
    try:
        location = request.form['location']  # Get location from form input
        daily_weather, hourly_weather, lat, lon = get_weather(location)  # Get weather data
        current_date = datetime.now()  # Get current date and time
        all_dates = [current_date + timedelta(days=i) for i in range(0, 5)]  # Generate dates for next 5 days
        
        combined_data = list(zip(all_dates, daily_weather))  # Combine dates with daily weather data

        if daily_weather:
            return render_template('home.html', daily_weather=daily_weather, hourly_weather=hourly_weather, today=current_date, combined_data=combined_data, lat=lat, lng=lon, error=None)
        else:
            return render_template('home.html', daily_weather=None, hourly_weather=None, today=current_date, combined_data=[], lat=lat, lng=lon, error="Location not found or weather data not available")
    except Exception as e:
        print("Error:", e)  # Debugging statement
        return render_template('home.html', daily_weather=None, hourly_weather=None, today=datetime.now(), combined_data=[], error="Error processing location")

# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Create instance of login form
    if form.validate_on_submit():  # Check if form is submitted and valid
        user = User.query.filter_by(username=form.username.data).first()  # Query user from database
        if user and user.check_password(form.password.data):  # Check if user exists and password is correct
            session['user_id'] = user.id  # Store user ID in session
            session['username'] = user.username  # Store username in session
            session['location'] = user.location  # Store user location in session
            flash('Login successful', 'success')  # Flash message for successful login
            return redirect(url_for('home'))  # Redirect to home page
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')  # Flash message for failed login
    return render_template('login.html', form=form)  # Render login form template

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = createAccount()  # Create instance of registration form
    if form.validate_on_submit():  # Check if form is submitted and valid
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()  # Check if user already exists
        if existing_user:
            flash('Username or email already exists. Please choose another.', 'danger')  # Flash message for existing user
        else:
            user = User(username=form.username.data, email=form.email.data, location=form.location.data)  # Create new user object
            user.set_password(form.password.data)  # Set user password
            db.session.add(user)  # Add user to database session
            db.session.commit()  # Commit changes to database
            flash('Your account has been created! You are now able to log in', 'success')  # Flash message for successful registration
            return redirect(url_for('login'))  # Redirect to login page
    else:
        if request.method == 'POST':
            print('Form validation failed')  # Debugging statement
            print(form.errors)  # Print form validation errors
    return render_template('register.html', form=form)  # Render registration form template

# Function to fetch weather data
def get_weather(location):
    geolocator = Nominatim(user_agent="weather_app")  # Create geolocator object
    location_data = geolocator.geocode(location)  # Get location data from geocoder

    if location_data:
        lat = location_data.latitude  # Get latitude
        lng = location_data.longitude  # Get longitude

        # Fetching daily weather data for the next 7 days
        daily_weather_url = f'https://api.tomorrow.io/v4/timelines?apikey={API_KEY}&location={lat},{lng}&fields=temperature,humidity,windSpeed,weatherCode&timesteps=1d&units=metric&timezone=auto'
        daily_response = requests.get(daily_weather_url)  # Send HTTP GET request
        daily_weather_data = daily_response.json()  # Parse JSON response

        # Fetching hourly weather data for the next 6 hours
        hourly_weather_url = f'https://api.tomorrow.io/v4/timelines?apikey={API_KEY}&location={lat},{lng}&fields=temperature,humidity,windSpeed,weatherCode&timesteps=1h&units=metric&timezone=auto'
        hourly_response = requests.get(hourly_weather_url)  # Send HTTP GET request
        hourly_weather_data = hourly_response.json()  # Parse JSON response

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
                formatted_time = datetime.strptime(time,
                "%Y-%m-%dT%H:%M:%S%z").strftime("%H:%M")
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

# Entry point of the application
if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode