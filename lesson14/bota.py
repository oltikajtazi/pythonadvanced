
import warnings
warnings.filterwarnings("ignore")

import plotly.express as px
import pandas as pd
from matplotlib import pyplot as plt

# Read CSV file
df = pd.read_csv("avgIQpercountry.csv")

# Clean population column
df['Population - 2023'] = (
    df['Population - 2023']
    .str.replace(',', '')
    .astype(float)
)

print(df.info())

# Create world map
fig = px.scatter_geo(
    df,
    locations='Country',
    locationmode='country names',
    hover_name='Country',
    size='Average IQ',
    size_max=20,
    template='plotly_dark',
    title='Average IQ by Country'
)

fig.show()