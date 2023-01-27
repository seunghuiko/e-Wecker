import requests
import pyttsx3

# API key for OpenWeather API
api_key = "bbdfb34fb97b47d43ed9b09f8bd7f7fb"

# API endpoint for Berlin weather forecast
url = f"http://api.openweathermap.org/data/2.5/weather?q=Berlin&appid=bbdfb34fb97b47d43ed9b09f8bd7f7fb"

# Make API request
response = requests.get(url)
data = response.json()

# Extract temperature and humidity from API response
temperature = data["main"]["temp"]
humidity = data["main"]["humidity"]

# Print temperature and humidity
print(f"Temperature: {temperature - 273.15}°C")
print(f"Humidity: {humidity}%")

# Check if it will rain and print hint
if "rain" in data:
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('voice', 'english-us')
    engine.say("Bring an umbrella today!")
    engine.runAndWait()
    print("Take an umbrella today!")
    
else:
    print("No need for an umbrella today.")
