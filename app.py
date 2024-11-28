import pandas as pd
import requests
import json
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

# === Data Loading ===

# Load Main.csv dataset containing engagement data by country
main_url = "https://raw.githubusercontent.com/AidaCPL/INFOSCI301_Final_Project/main/Data/Main.csv"
df_main = pd.read_csv(main_url)

# Load Climate-FEVER dataset with climate misinformation claims and evidence
climate_url = "https://raw.githubusercontent.com/AidaCPL/INFOSCI301_Final_Project/main/Data/climate-fever-dataset-r1.jsonl"
climate_data = []
response = requests.get(climate_url, stream=True)
for line in response.iter_lines():
    if line:
        climate_data.append(json.loads(line))
df_climate = pd.DataFrame(climate_data)

# Load Politifact fake and real news datasets
fake_url = "https://raw.githubusercontent.com/AidaCPL/INFOSCI301_Final_Project/main/Data/politifact_fake.csv"
real_url = "https://raw.githubusercontent.com/AidaCPL/INFOSCI301_Final_Project/main/Data/politifact_real.csv"
df_fake = pd.read_csv(fake_url)
df_real = pd.read_csv(real_url)

# === Data Processing ===

# Compute average engagement levels per country
df_engagement = df_main[['Country', 'political', 'science', 'business']].groupby('Country').mean().reset_index()

# Add "type" column to distinguish fake and real news
df_fake['type'] = 'Fake'
df_real['type'] = 'Real'

# Combine fake and real news datasets
df_news = pd.concat([df_fake[['title', 'type']], df_real[['title', 'type']]])

# Assign news articles to valid countries cyclically
countries = df_engagement['Country'].tolist()
df_news['Country'] = pd.Series(countries * (len(df_news) // len(countries) + 1))[:len(df_news)]

# Merge engagement data with news types on the 'Country' column
df_plot = df_engagement.merge(df_news, on='Country', how='inner')

# Prepare data for visualization: Melt engagement columns
df_melted = df_plot.melt(
    id_vars=['Country', 'type', 'title'],  # Include news title and type
    value_vars=['political', 'science', 'business'],  # Engagement types
    var_name='Engagement Type',
    value_name='Engagement Level'
)

# === Dash App Setup ===

# Create a Dash app
app = Dash(__name__)

# Create a bar chart figure
fig = px.bar(
    df_melted,
    x='Country',
    y='Engagement Level',
    color='Engagement Type',
    barmode='group',
    facet_col='type',
    hover_data=['title'],
    title='Engagement Levels Across Countries by News Type (Fake vs Real)',
    labels={
        'Engagement Level': 'Average Engagement Level',
        'Country': 'Country',
        'Engagement Type': 'Type of Engagement',
        'type': 'News Type'
    },
    template='plotly_white'
)

fig.update_layout(
    xaxis_title="Country",
    yaxis_title="Engagement Level",
    legend_title="Engagement Type",
    title_x=0.5,
    height=800,
)

# Layout for the app
app.layout = html.Div(children=[
    html.H1("Engagement Levels Across Countries", style={'text-align': 'center'}),
    dcc.Graph(figure=fig)
])

if __name__ == "__main__":
    app.run_server(debug=True)