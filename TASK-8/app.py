from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


@app.route("/")
def home():
    return jsonify({
        "message": "Weather API is running",
        "usage": "/weather?city=London"
    })


@app.route("/weather", methods=["GET"])
def get_weather():
    city = request.args.get("city")

    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()

    if response.status_code != 200:
        return jsonify({
            "error": data.get("message", "Something went wrong")
        }), response.status_code

    weather_info = {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "weather": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"]
    }

    return jsonify(weather_info)


if __name__ == "__main__":
    app.run(debug=True)