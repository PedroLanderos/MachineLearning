# guardar como evalua_modelo.py
import sys, pandas as pd, numpy as np, matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

csv = sys.argv[1] if len(sys.argv)>1 else "weather_2024-11-10_to_2025-11-10.csv"
df = pd.read_csv(csv).sort_values("timestamp")
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

cut = int(len(df)*0.8)
Xtr, Xte, ytr, yte = X.iloc[:cut], X.iloc[cut:], y.iloc[:cut], y.iloc[cut:]
m = GradientBoostingRegressor(loss="huber", alpha=0.9, n_estimators=1200,
    learning_rate=0.035, max_depth=3, subsample=0.85, max_features="sqrt",
    validation_fraction=0.1, n_iter_no_change=20, random_state=42).fit(Xtr,ytr)

p = m.predict(Xte)
mae = mean_absolute_error(yte,p); rmse = mean_squared_error(yte,p, squared=False)
print(f"MAE: {mae:.3f} °C | RMSE: {rmse:.3f} °C | N test: {len(yte)}")

plt.figure(figsize=(9,4)); plt.plot(yte.values, label="Real"); plt.plot(p, label="Pred")
plt.title(f"Test MAE={mae:.2f}  RMSE={rmse:.2f}"); plt.xlabel("Horas (test)"); plt.ylabel("°C"); plt.legend(); plt.tight_layout()
plt.savefig("eval_pred_vs_real.png"); print("Gráfica guardada: eval_pred_vs_real.png")
