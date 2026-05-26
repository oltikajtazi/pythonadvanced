from matplotlib import pyplot as plt
import pandas as pd


df = pd.read_csv('avgIQpercountry.csv')

avg_iq_by_continent = df.groupby('continent')["Average IQ"].mean()


plt.figure(figsize=(10,6))

avg_iq_by_continent.plot(kind="line",marker="0",color="skyblue")

plt.show()