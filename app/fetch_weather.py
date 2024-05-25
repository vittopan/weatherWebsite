import requests
from geopy.geocoders import Nominatim

def get_weather(location):
    API_KEY = 'GWYm9XH0pw9IN0pk72zylGTmSZ7b1LBX'  # Replace with your actual API key

    # Geocoding using Nominatim (OpenStreetMap)
    geolocator = Nominatim(user_agent="weather_app")
    location_data = geolocator.geocode(location)

    if location_data:
        lat = location_data.latitude
        lng = location_data.longitude

        # Fetching weather data
        weather_url = f'https://api.tomorrow.io/v4/timelines?apikey={API_KEY}&location={lat},{lng}&fields=temperature,humidity,windSpeed,weatherCode&timesteps=current&units=metric&timezone=auto'
        response = requests.get(weather_url)
        weather_data = response.json()

        if weather_data.get('data'):
            current_weather = weather_data['data']['timelines'][0]['intervals'][0]['values']
            temperature = current_weather['temperature']
            humidity = current_weather['humidity']
            wind_speed = current_weather['windSpeed']
            weather_code = current_weather['weatherCode']

            print(f"Weather in {location_data.address}:")
            print(f"Temperature: {temperature} °C")
            print(f"Humidity: {humidity} %")
            print(f"Wind Speed: {wind_speed} m/s")
            print(f"Weather Code: {weather_code}")
        else:
            print("Weather data not available.")
    else:
        print("Location not found.")

def main():
    location = input("Enter a city name: ")
    get_weather(location)

if __name__ == "__main__":
    main()



