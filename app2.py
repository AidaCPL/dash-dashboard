import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.express as px
from dash import Dash, dcc, html
import pandas as pd
import requests
import json
import plotly.express as px
import plotly.graph_objects as go
from sklearn.feature_extraction.text import CountVectorizer


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

# Preparing a dataset for clustering: Combining engagement and country-specific details
# Assuming "Country" is a key feature in df_main
engagement_data = df_main[['Country', 'fb', 'tw', 'sn', 'ig']]  # Social media engagement columns
engagement_data = engagement_data.groupby('Country').mean().reset_index()

# Scaling data for clustering
scaler = StandardScaler()
scaled_engagement = scaler.fit_transform(engagement_data[['fb', 'tw', 'sn', 'ig']])

# Applying KMeans clustering
kmeans = KMeans(n_clusters=3, random_state=42)
engagement_data['Cluster'] = kmeans.fit_predict(scaled_engagement)

# Create a Dash app
app = Dash(__name__)

# Create a scatter plot figure
fig = px.scatter(
    engagement_data,
    x='fb',  # Engagement on Facebook
    y='tw',  # Engagement on Twitter
    color='Cluster',  # Color by cluster
    hover_data=['Country'],  # Show country on hover
    title="Clustering Visualization of Engagement with Misinformation Across Countries",
    labels={
        'fb': 'Facebook Engagement',
        'tw': 'Twitter Engagement'
    },
    template='plotly_white'
)

fig.update_layout(
    xaxis_title="Average Facebook Engagement",
    yaxis_title="Average Twitter Engagement",
    legend_title="Cluster"
)

# Define the layout for the app
app.layout = html.Div(children=[
    html.H1("Engagement Clustering Dashboard", style={'text-align': 'center'}),
    dcc.Graph(figure=fig)
])

if __name__ == "__main__":
    app.run_server(debug=True)
