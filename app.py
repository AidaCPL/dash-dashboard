import dash
from dash import dcc, html
import pandas as pd
import plotly.graph_objects as go
import networkx as nx

# Load the dataset
edges_file = 'edges.csv'  # Replace with your file path
edges_data = pd.read_csv(edges_file)

# Create the graph
G = nx.DiGraph()  # Directed graph
for _, row in edges_data.iterrows():
    G.add_edge(row['Source'], row['Target'], weight=row['Weight'], label=row['Label'])

# Extract node positions using a layout algorithm
pos = nx.spring_layout(G, seed=42)  # Spring layout for visualization
for node in G.nodes:
    G.nodes[node]['pos'] = pos[node]

# Create edge traces for visualization
edge_traces = []
for edge in G.edges(data=True):
    x0, y0 = G.nodes[edge[0]]['pos']
    x1, y1 = G.nodes[edge[1]]['pos']
    color = 'green' if edge[2]['label'] == 'SUPPORTS' else 'red'  # Color based on Label
    edge_traces.append(
        go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            line=dict(width=edge[2]['weight'], color=color),
            mode='lines'
        )
    )

# Create node traces for visualization
node_trace = go.Scatter(
    x=[G.nodes[node]['pos'][0] for node in G.nodes],
    y=[G.nodes[node]['pos'][1] for node in G.nodes],
    text=[node for node in G.nodes],
    mode='markers+text',
    marker=dict(
        size=10,
        color='blue',
        line=dict(width=2, color='black')
    ),
    textposition="top center"
)

# Initialize Dash app
app = dash.Dash(__name__)

# Build the layout
app.layout = html.Div([
    html.H1("Network Graph Visualization", style={'text-align': 'center'}),
    dcc.Graph(
        id='network-graph',
        figure=go.Figure(data=edge_traces + [node_trace])
            .update_layout(
                showlegend=False,
                hovermode='closest',
                margin=dict(b=0, l=0, r=0, t=0),
                xaxis=dict(showgrid=False, zeroline=False),
                yaxis=dict(showgrid=False, zeroline=False)
            )
    )
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)