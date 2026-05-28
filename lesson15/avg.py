import pandas as pd
import plotly.express as px
import os

# Show current folder (helps debugging)
print("Current folder:", os.getcwd())
print("Files here:", os.listdir())

# Load file (make sure CSV is in same folder as script)
df = pd.read_csv("weather_tokyo_data.csv")

# Convert temperature to numeric (fixes your earlier error)
df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")

# Remove bad rows
df = df.dropna(subset=["temperature"])

# Average temperature
average_temp = df["temperature"].mean()
print("Average Temperature:", round(average_temp, 2))

# Max / Min
print("Highest Temperature:", df["temperature"].max())
print("Lowest Temperature:", df["temperature"].min())

# Simple time graph
df["day"] = df.index

import matplotlib.pyplot as plt

plt.figure(figsize=(12, 5))
plt.plot(df["day"], df["temperature"], color="red")
plt.title("Temperature Changes Over Time")
plt.xlabel("Days")
plt.ylabel("Temperature")
plt.grid(True)
plt.show()


df["country"] = "Japan"

fig = px.choropleth(
    df,
    locations="country",
    locationmode="country names",
    color="temperature",
    hover_name="country",
    color_continuous_scale="RdYlBu_r",
    title="Temperature Map"
)

fig.show()