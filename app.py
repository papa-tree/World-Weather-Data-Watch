from flask import Flask, request, render_template
import requests
import cohere  # Import the Cohere library

# Initialize Flask app
app = Flask(__name__)

# OpenWeatherMap API setup
API_KEY_WEATHER = ""  # Replace with your OpenWeatherMap API key
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

# Cohere AI setup
COHERE_API_KEY = ""  # Replace with your Cohere API key
co = cohere.Client(COHERE_API_KEY)

# Fetch weather data from OpenWeatherMap
def fetch_weather_data(location):
    params = {"q": location, "appid": API_KEY_WEATHER, "units": "metric"}
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Generate advice using Cohere AI
def generate_advice_with_cohere(weather_data, location):
    if not weather_data:
        return f"Chatbot: Couldn't fetch weather data for {location}. Please check the location name."

    # Extract weather details
    weather = weather_data["weather"][0]["description"]
    temp = weather_data["main"]["temp"]
    humidity = weather_data["main"]["humidity"]
    wind_speed = weather_data["wind"]["speed"]

    # Prepare prompt for Cohere AI
    prompt = f"""
    Based on the following weather details:
    - Location: {location}
    - Weather: {weather}
    - Temperature: {temp}°C
    - Humidity: {humidity}%
    - Wind Speed: {wind_speed} km/h
    
    Provide the weather data, for example, the numerical temperature humidity and wind speed, to the user and give them advice on what to wear or do today.
    For example, if it's sunny and warm, suggest wearing light clothing and sunglasses. If it's rainy, suggest carrying an umbrella and wearing waterproof shoes.
    """
    
    try:
        # Call Cohere's generate endpoint
        response = co.generate(
            model='command-light',  # Use the "xlarge" model provided by Cohere
            prompt=prompt,
            max_tokens=150,  # Adjust response length as needed
            temperature=0.7,  # Control creativity level
        )
        return response.generations[0].text.strip()
    except Exception as e:
        return f"Chatbot Error: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_advice', methods=['POST'])
def get_advice():
    location = request.form.get('location')
    if not location:
        return render_template('index.html', error="Please enter a location.")
    
    weather_data = fetch_weather_data(location)
    advice = generate_advice_with_cohere(weather_data, location)
    return render_template('results.html', location=location, advice=advice)

if __name__ == '__main__':
    app.run(debug=True)