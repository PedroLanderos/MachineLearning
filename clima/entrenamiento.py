# guardar como entrenamiento.py
import sys, pandas as pd, numpy as np, pickle
from sklearn.ensemble import GradientBoostingRegressor

df = pd.read_csv(sys.argv[1]).sort_values("timestamp")
t = pd.to_datetime(df["timestamp"])
df["hour"], df["day"], df["month"] = t.dt.hour, t.dt.dayofyear, t.dt.month
for c,m in [("hour",24),("day",365),("month",12)]:
    df[f"sin_{c}"], df[f"cos_{c}"] = np.sin(2*np.pi*df[c]/m), np.cos(2*np.pi*df[c]/m)

s = df["temperature_2m"]
df["lag1"], df["lag2"], df["lag3"] = s.shift(1), s.shift(2), s.shift(3)
df["roll3"]   = s.rolling(3).mean()
df["dpress3"] = df["pressure_msl"] - df["pressure_msl"].shift(3)
df["dcloud3"] = df["cloud_cover"]  - df["cloud_cover"].shift(3)
df["td_spread"] = df["temperature_2m"] - df["dew_point_2m"]

cols = ["sin_hour","cos_hour","sin_day","cos_day","sin_month","cos_month",
        "relative_humidity_2m","dew_point_2m","pressure_msl","cloud_cover",
        "shortwave_radiation","wind_speed_10m","wind_direction_10m",
        "lag1","lag2","lag3","roll3","dpress3","dcloud3","td_spread"]
df = df.dropna()
X, y = df[cols], df["temperature_2m"]

m = GradientBoostingRegressor(loss="huber", alpha=0.9, n_estimators=1200,
    learning_rate=0.035, max_depth=3, subsample=0.85, max_features="sqrt",
    validation_fraction=0.1, n_iter_no_change=20, random_state=42).fit(X,y)

pickle.dump((m, cols), open("modelo_temp.pkl","wb"))
print("Modelo entrenado y guardado como modelo_temp.pkl")
