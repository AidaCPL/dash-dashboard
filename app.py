import pandas as pd
import dash
import dash_cytoscape as cyto
from dash import html, dcc
import networkx as nx
import os

# Load the dataset
file_path = "data/edges_simplified_no_stopwords.csv"
edges = pd.read_csv(file_path)

# Separate edges based on the "Label"
supports_edges = edges[edges['Label'] == 'SUPPORTS']
refutes_edges = edges[edges['Label'] == 'REFUTES']

# Create two graphs: one for SUPPORTS and one for REFUTES
G_supports = nx.DiGraph()
G_refutes = nx.DiGraph()

# Add edges and nodes for SUPPORTS
for _, row in supports_edges.iterrows():
    G_supports.add_edge(row['Source'], row['Target'], weight=row['Weight'])

# Add edges and nodes for REFUTES
for _, row in refutes_edges.iterrows():
    G_refutes.add_edge(row['Source'], row['Target'], weight=row['Weight'])

# Find common nodes between the two graphs
common_nodes = set(G_supports.nodes()).intersection(set(G_refutes.nodes()))

# Reassign common nodes
def reassign_common_nodes(common_nodes, G_supports, G_refutes):
    reassigned_nodes = {}
    for node in common_nodes:
        supports_weight = sum(data["weight"] for _, data in G_supports[node].items())
        refutes_weight = sum(data["weight"] for _, data in G_refutes[node].items())
        reassigned_nodes[node] = "supports" if supports_weight >= refutes_weight else "refutes"
    return reassigned_nodes

# Reassign common nodes
reassigned_nodes = reassign_common_nodes(common_nodes, G_supports, G_refutes)

# Create Cytoscape elements with adjusted node sizes
def create_elements(graph, cluster_label, reassigned_nodes, scale_factor=1.0):
    elements = []
    node_sizes = {}

    for node in graph.nodes():
        if node in reassigned_nodes:
            cluster_label = reassigned_nodes[node]
        base_size = sum(data["weight"] for _, data in graph[node].items())
        normalized_size = base_size ** 0.5 * 5  # Square root for less drastic differences, then scale
        scaled_size = normalized_size * scale_factor  # Apply scaling
        node_sizes[node] = normalized_size
        elements.append({
            "data": {
                "id": node,
                "label": node,
                "group": cluster_label,
                "base_size": normalized_size,  # Keep the original size static
                "size": max(5, scaled_size)  # Scale size
            }
        })

    for source, target, data in graph.edges(data=True):
        elements.append({
            "data": {
                "source": source,
                "target": target,
                "weight": data["weight"]
            }
        })

    return elements

# Generate base elements for the Cytoscape graph
supports_elements = create_elements(G_supports, "supports", reassigned_nodes)
refutes_elements = create_elements(G_refutes, "refutes", reassigned_nodes)

# Dash app setup
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("Network Graph of most used words in Fake vs. Real Climate News", style={"textAlign": "center"}),

    # Legend
    html.Div(
        children=[
            html.P("Legend:"),
            html.Ul([
                html.Li("Blue Nodes: SUPPORTS Cluster"),
                html.Li("Red Nodes: REFUTES Cluster"),
                html.Li("Node Size: Proportional to the weighted degree (importance)"),
            ]),
        ],
        style={"padding": "10px", "border": "1px solid black", "marginBottom": "10px"}
    ),

    # Dropdown to change node layout
    html.Label("Choose Layout:"),
    dcc.Dropdown(
        id='layout-dropdown',
        options=[
            {'label': 'Force-Directed (Cose)', 'value': 'cose'},
            {'label': 'Hierarchical (Breadthfirst)', 'value': 'breadthfirst'}
        ],
        value='cose',  # Default layout
        style={'width': '300px', 'marginBottom': '10px'}
    ),

    # Slider to scale node sizes
    html.Label("Adjust Node Size:"),
    dcc.Slider(
        id='node-size-slider',
        min=0.5,
        max=3,
        step=0.1,
        value=1.0,
        marks={i: str(i) for i in range(1, 4)},
        tooltip={"placement": "bottom", "always_visible": True},
    ),

    # Cytoscape graph
    cyto.Cytoscape(
        id='network-graph',
        elements=supports_elements + refutes_elements,  # Combine elements
        layout={'name': 'cose'},
        style={'width': '100%', 'height': '800px'},
        stylesheet=[
            {"selector": "node[group='supports']", "style": {"background-color": "blue", "shape": "ellipse", "width": "data(size)", "height": "data(size)"}},
            {"selector": "node[group='refutes']", "style": {"background-color": "red", "shape": "triangle", "width": "data(size)", "height": "data(size)"}},
            {"selector": "edge", "style": {"line-color": "gray", "width": 2, "target-arrow-shape": "triangle"}}
        ]
    )
])

# Callback to update layout dynamically
@app.callback(
    dash.dependencies.Output('network-graph', 'layout'),
    [dash.dependencies.Input('layout-dropdown', 'value')]
)
def update_layout(selected_layout):
    return {'name': selected_layout}

# Callback to adjust node sizes based on the slider
@app.callback(
    dash.dependencies.Output('network-graph', 'elements'),
    [dash.dependencies.Input('node-size-slider', 'value')]
)
def update_node_sizes(scale_factor):
    supports_elements = create_elements(G_supports, "supports", reassigned_nodes, scale_factor)
    refutes_elements = create_elements(G_refutes, "refutes", reassigned_nodes, scale_factor)
    return supports_elements + refutes_elements

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port)
