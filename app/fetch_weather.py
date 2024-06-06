import requests
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta

def get_weather(location):
    API_KEY = 'GWYm9XH0pw9IN0pk72zylGTmSZ7b1LBX'  # Replace with your actual API key

    # Geocoding using Nominatim (OpenStreetMap)
    geolocator = Nominatim(user_agent="weather_app")
    location_data = geolocator.geocode(location)

    if location_data:
        lat = location_data.latitude
        lng = location_data.longitude

        # Fetching weather data for the next 6 hours
        weather_url = f'https://api.tomorrow.io/v4/timelines?apikey={API_KEY}&location={lat},{lng}&fields=temperature,humidity,windSpeed,weatherCode&timesteps=1h&units=metric&timezone=auto'
        response = requests.get(weather_url)
        weather_data = response.json()

        if weather_data.get('data'):
            six_hour_weather = []
            intervals = weather_data['data']['timelines'][0]['intervals'][:6]  # Limit to the next 6 hours
            for interval in intervals:
                date = interval['startTime']
                # Format the date to include hour and minute
                formatted_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z").strftime("%d-%b %H:%M")

                values = interval['values']
                hourly_weather = {
                    'time': formatted_date,
                    'temperature': values['temperature'],
                    'humidity': values['humidity'],
                    'wind_speed': values['windSpeed'],
                    'weather_code': values['weatherCode']
                }
                six_hour_weather.append(hourly_weather)

            return six_hour_weather
        else:
            print("Weather data not available.")
            return None
    else:
        print("Location not found.")
        return None

def main():
    location = input("Enter a city name: ")
    weather_forecast = get_weather(location)
    if weather_forecast:
        for hour in weather_forecast:
            print(f"Time: {hour['time']}")
            print(f"Temperature: {hour['temperature']}°C")
            print(f"Humidity: {hour['humidity']}%")
            print(f"Wind Speed: {hour['wind_speed']} km/h")
            print()
if __name__ == "__main__":
    main()
