# guardar como prediccion.py
import sys, pickle, pandas as pd, numpy as np, requests
lat, lon = 19.43, -99.13
fecha, hora = sys.argv[1], sys.argv[2]
t = pd.to_datetime(f"{fecha} {hora}")

m, cols = pickle.load(open("modelo_temp.pkl","rb"))
v = "temperature_2m,relative_humidity_2m,dew_point_2m,pressure_msl,cloud_cover,shortwave_radiation,wind_speed_10m,wind_direction_10m"
u = (f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
     f"&start_date={(t-pd.Timedelta(days=1)).date()}&end_date={fecha}&hourly={v}&timezone=America%2FMexico_City")
df = pd.DataFrame(requests.get(u).json()["hourly"]).rename(columns={"time":"timestamp"}).sort_values("timestamp")
df["timestamp"] = pd.to_datetime(df["timestamp"])

row = df[df["timestamp"] == pd.to_datetime(f"{fecha} {hora}:00")]
if row.empty: raise SystemExit("No se encontró esa hora en el API (revisa fecha/hora).")
i = row.index[0]
if i < 3:     raise SystemExit("No hay suficientes horas previas para lags.")

lag1, lag2, lag3 = [df["temperature_2m"].iloc[i-j] for j in (1,2,3)]
roll3   = df["temperature_2m"].iloc[i-2:i+1].mean()
dpress3 = df["pressure_msl"].iloc[i] - df["pressure_msl"].iloc[i-3]
dcloud3 = df["cloud_cover"].iloc[i]  - df["cloud_cover"].iloc[i-3]
td_spread = row["temperature_2m"].iloc[0] - row["dew_point_2m"].iloc[0]

hum, dew, pres, cloud, swr, wind, wdir = row[["relative_humidity_2m","dew_point_2m","pressure_msl","cloud_cover","shortwave_radiation","wind_speed_10m","wind_direction_10m"]].iloc[0]
s = lambda x,m: (np.sin(2*np.pi*x/m), np.cos(2*np.pi*x/m))
sh,ch = s(t.hour,24); sd,cd = s(t.dayofyear,365); sm,cm = s(t.month,12)

X = pd.DataFrame([[sh,ch,sd,cd,sm,cm,hum,dew,pres,cloud,swr,wind,wdir,lag1,lag2,lag3,roll3,dpress3,dcloud3,td_spread]], columns=cols)
print(round(m.predict(X)[0],2), "°C")
