# guardar como fetch_weather_csv.py
import sys, requests, pandas as pd
lat, lon = 19.43, -99.13
start, end = sys.argv[1], sys.argv[2]
v = "temperature_2m,relative_humidity_2m,dew_point_2m,pressure_msl,cloud_cover,shortwave_radiation,wind_speed_10m,wind_direction_10m"
u = (f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
     f"&start_date={start}&end_date={end}&hourly={v}&timezone=America%2FMexico_City")
df = pd.DataFrame(requests.get(u).json()["hourly"]).rename(columns={"time":"timestamp"})
df.to_csv(f"weather_{start}_to_{end}.csv", index=False)
print(f"Archivo guardado: weather_{start}_to_{end}.csv")
