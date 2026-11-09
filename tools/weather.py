import os
import re
from datetime import datetime

CITY_COORDINATES = {
    "Mumbai": (19.0760, 72.8777),
    "Pune": (18.5204, 73.8567),
    "Hyderabad": (17.3850, 78.4867),
    "Bengaluru": (12.9716, 77.5946),
    "Ahmedabad": (23.0225, 72.5714),
}

def get_weather(city, date_str):
    mode = os.environ.get("WEATHER_MODE", "stub").lower()

    if city not in CITY_COORDINATES:
        return {"ok": False, "error": f"unsupported city: {city}"}

    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        return {"ok": False, "error": f"invalid date format: {date_str}"}

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return {"ok": False, "error": f"invalid calendar date: {date_str}"}

    if mode == "live":
        try:
            import requests
            lat, lon = CITY_COORDINATES[city]
            url = "https://archive-api.open-meteo.com/v1/archive"
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": date_str,
                "end_date": date_str,
                "timezone": "Asia/Kolkata",
                "daily": "temperature_2m_mean,relative_humidity_2m_mean,wind_speed_10m_max,precipitation_sum",
            }
            res = requests.get(url, params=params, timeout=5)
            if res.status_code == 200:
                data = res.json()
                daily = data.get("daily", {})
                return {
                    "ok": True,
                    "city": city,
                    "date": date_str,
                    "mode": "live",
                    "temperature_c": float(daily.get("temperature_2m_mean", [0.0])[0]),
                    "humidity_pct": float(daily.get("relative_humidity_2m_mean", [0.0])[0]),
                    "wind_kmh": float(daily.get("wind_speed_10m_max", [0.0])[0]),
                    "rain_mm": float(daily.get("precipitation_sum", [0.0])[0]),
                }
            return {"ok": False, "error": f"live weather api failed with status code {res.status_code}"}
        except Exception as e:
            return {"ok": False, "error": f"live weather api request error: {str(e)}"}

    # Deterministic stub mode
    doy = dt.timetuple().tm_yday
    n = len(city)
    temp = float(20 + (n + doy) % 15)
    humidity = float(40 + (3 * n + doy) % 50)
    wind = float(5 + doy % 10)
    rain = 6.5 if doy % 4 == 0 else 0.0

    return {
        "ok": True,
        "city": city,
        "date": date_str,
        "mode": "stub",
        "temperature_c": temp,
        "humidity_pct": humidity,
        "wind_kmh": wind,
        "rain_mm": rain,
    }