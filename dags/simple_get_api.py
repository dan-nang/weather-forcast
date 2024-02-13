import requests
from datetime import datetime, timedelta

def fetch_hourly_forecast():
    # API endpoint for hourly forecast
    endpoint = "https://api.openweathermap.org/data/2.5/forecast"
    
    # Set the query parameters
    params = {
        "q": 'Jakarta',
        "appid":'04e28a3f5f628d0895a3523b43a5a634',
        "units": "metric"  # Use "imperial" for Fahrenheit
    }
    
    # Make the API request
    response = requests.get(endpoint, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        
        # Get tomorrow's date
        tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Filter hourly forecast data for tomorrow
        hourly_forecast = [forecast for forecast in data["list"] if forecast["dt_txt"].startswith(tomorrow_date)]
        
        return hourly_forecast
    else:
        print("Failed to fetch weather data:", response.status_code)
        return None

# Fetch hourly forecast data for tomorrow
hourly_forecast = fetch_hourly_forecast()

# Print all data in api
print(hourly_forecast)

# Print hourly forecast data
# if hourly_forecast:
#     for forecast in hourly_forecast:
#         forecast_time = datetime.fromtimestamp(forecast["dt"]).strftime("%Y-%m-%d %H:%M:%S")
#         temperature = forecast["main"]["temp"]
#         description = forecast["weather"][0]["description"]
#         print(f"At {forecast_time}: Temperature: {temperature}°C, Description: {description}")