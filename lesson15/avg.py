import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import os

# -----------------------------
# LOAD DATA
# -----------------------------
print("Current folder:", os.getcwd())
print("Files here:", os.listdir())

df = pd.read_csv("weather_tokyo_data.csv")

# -----------------------------
# CLEAN DATA
# -----------------------------
df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
df = df.dropna(subset=["temperature"])

# If there is a date column, convert it
if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"])
else:
    # fallback if no date column exists
    df["date"] = pd.date_range(start="2024-01-01", periods=len(df), freq="D")

df["month"] = df["date"].dt.month
df["month_name"] = df["date"].dt.strftime("%B")

# -----------------------------
# 1. TEMPERATURE OVERVIEW
# -----------------------------
avg_temp = df["temperature"].mean()
print("\n=== TEMPERATURE OVERVIEW ===")
print("Average Temperature:", round(avg_temp, 2))

# -----------------------------
# 2. MONTHLY TEMPERATURE
# -----------------------------
monthly_avg = df.groupby("month_name")["temperature"].mean().reindex([
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
])

print("\n=== MONTHLY AVERAGES ===")
print(monthly_avg)

# Bar plot
fig1 = px.bar(
    x=monthly_avg.index,
    y=monthly_avg.values,
    labels={"x": "Month", "y": "Avg Temperature"},
    title="Monthly Average Temperature in Tokyo",
    color=monthly_avg.values,
    color_continuous_scale="RdYlBu_r"
)
fig1.show()

# -----------------------------
# 3. HOTTEST & COLDEST DAYS
# -----------------------------
hottest = df.loc[df["temperature"].idxmax()]
coldest = df.loc[df["temperature"].idxmin()]

print("\n=== HOTTEST DAY ===")
print(hottest)

print("\n=== COLDEST DAY ===")
print(coldest)

# -----------------------------
# 4. TEMPERATURE TREND (LINE GRAPH)
# -----------------------------
df = df.sort_values("date")

plt.figure(figsize=(14, 6))
plt.plot(df["date"], df["temperature"], color="red", linewidth=1)
plt.title("Temperature Trend Over Time (Tokyo)")
plt.xlabel("Date")
plt.ylabel("Temperature")
plt.grid(True)
plt.tight_layout()
plt.show()

# -----------------------------
# 5. SEASONAL AVERAGE TEMPERATURE
# -----------------------------
def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Autumn"

df["season"] = df["month"].apply(get_season)

seasonal_avg = df.groupby("season")["temperature"].mean()

print("\n=== SEASONAL AVERAGES ===")
print(seasonal_avg)

fig2 = px.bar(
    x=seasonal_avg.index,
    y=seasonal_avg.values,
    labels={"x": "Season", "y": "Avg Temperature"},
    title="Seasonal Average Temperature",
    color=seasonal_avg.values,
    color_continuous_scale="RdYlBu_r"
)

fig2.show()

# -----------------------------
# OPTIONAL: SIMPLE CLEAN MAP (FIXED)
# -----------------------------
df["country"] = "Japan"

fig3 = px.scatter_geo(
    df,
    locations="country",
    locationmode="country names",
    color="temperature",
    title="Temperature Overview (Japan)",
    color_continuous_scale="RdYlBu_r"
)

fig3.show()