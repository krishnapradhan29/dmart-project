# Weather Tool Verification Tests

The tool `tools/weather.py` exposes `get_weather(city, date_str)` operating in `stub` mode by default.

### Test Case 1: Mumbai 2026-05-15 (Stub Check Value)
- **Call:** `get_weather("Mumbai", "2026-05-15")`
- **Output:**
```json
{
  "ok": true,
  "city": "Mumbai",
  "date": "2026-05-15",
  "mode": "stub",
  "temperature_c": 26.0,
  "humidity_pct": 43.0,
  "wind_kmh": 10.0,
  "rain_mm": 0.0
}