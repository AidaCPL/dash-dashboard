import pandas as pd
import dash
import dash_cytoscape as cyto
from dash import html, dcc
import networkx as nx

# Load the dataset (update the path to match your local file location)
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
        # Calculate total weight of edges connecting to SUPPORTS
        supports_weight = sum(
            data["weight"]
            for neighbor, data in G_supports[node].items()
            if neighbor in G_supports.nodes()
        )
        
        # Calculate total weight of edges connecting to REFUTES
        refutes_weight = sum(
            data["weight"]
            for neighbor, data in G_refutes[node].items()
            if neighbor in G_refutes.nodes()
        )
        
        # Assign to the class with the highest weight
        if supports_weight >= refutes_weight:
            reassigned_nodes[node] = "supports"
        else:
            reassigned_nodes[node] = "refutes"
    
    return reassigned_nodes

# Reassign common nodes
reassigned_nodes = reassign_common_nodes(common_nodes, G_supports, G_refutes)

# Create Cytoscape elements with scaled node size and edge thickness
def create_elements(graph, cluster_label, reassigned_nodes):
    elements = []

    for node in graph.nodes():
        # Check if the node is reassigned
        if node in reassigned_nodes:
            cluster_label = reassigned_nodes[node]
        # Scale node size by its degree (or weighted degree)
        node_size = sum(
            data["weight"] for _, data in graph[node].items()
        ) * 2  # Scaled multiplier
        node_data = {
            "id": node,
            "label": node,
            "group": cluster_label,
            "size": max(10, node_size),  # Minimum size of 10 for visibility
            "font_size": max(8, node_size // 2)  # Text size proportional to node size
        }
        elements.append({"data": node_data})

    # Add edges
    for source, target, data in graph.edges(data=True):
        edge_thickness = data["weight"]  # Use weight directly for edge thickness
        elements.append({
            "data": {
                "source": source,
                "target": target,
                "weight": data["weight"],
                "width": edge_thickness,  # Edge width based on weight
                "label": f"Weight: {data['weight']}"  # Hover text for edges
            }
        })

    return elements

# Generate elements for each cluster
supports_elements = create_elements(G_supports, "supports", reassigned_nodes)
refutes_elements = create_elements(G_refutes, "refutes", reassigned_nodes)

# Combine elements
all_elements = supports_elements + refutes_elements

# Dash app setup
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(
        children=[
            html.H1("Interactive Network Graph", style={"textAlign": "center"}),
            html.P("Legend:"),
            html.Ul([
                html.Li("Blue Nodes: SUPPORTS Cluster"),
                html.Li("Red Nodes: REFUTES Cluster"),
                html.Li("Node Size: Proportional to the weighted degree (importance)"),
                html.Li("Text Size: Proportional to the node size"),
                html.Li("Edge Thickness: Proportional to edge weight (strength of relationship)")
            ]),
            html.Label("Choose Layout:"),
            dcc.Dropdown(
                id='layout-dropdown',
                options=[
                    {'label': 'Force-Directed (Cose)', 'value': 'cose'},
                    {'label': 'Hierarchical (Breadthfirst)', 'value': 'breadthfirst'}
                ],
                value='cose',  # Default layout
                clearable=False,
                style={'width': '300px', 'marginBottom': '10px'}
            )
        ],
        style={"padding": "10px", "border": "1px solid black", "marginBottom": "10px"}
    ),
    cyto.Cytoscape(
        id='network-graph',
        elements=all_elements,
        layout={'name': 'cose'},  # Default layout
        style={'width': '100%', 'height': '800px'},
        stylesheet=[
            # Style nodes
            {
                "selector": "node[group='supports']",
                "style": {
                    "background-color": "blue",
                    "label": "data(label)",
                    "width": "data(size)",
                    "height": "data(size)",
                    "font-size": "data(font_size)"  # Text size proportional to node size
                }
            },
            {
                "selector": "node[group='refutes']",
                "style": {
                    "background-color": "red",
                    "label": "data(label)",
                    "width": "data(size)",
                    "height": "data(size)",
                    "font-size": "data(font_size)"  # Text size proportional to node size
                }
            },
            # Style edges
            {
                "selector": "edge",
                "style": {
                    "line-color": "gray",
                    "width": "data(width)",
                    "target-arrow-shape": "triangle",
                }
            },
        ]
    )
])

# Update layout dynamically
@app.callback(
    dash.dependencies.Output('network-graph', 'layout'),
    [dash.dependencies.Input('layout-dropdown', 'value')]
)
def update_layout(selected_layout):
    layout = {'name': selected_layout}
    if selected_layout == 'breadthfirst':
        layout['roots'] = '[id = "RootNode"]'  # Optionally specify a root node
    return layout

if __name__ == "__main__":
    app.run_server(debug=True, use_reloader=False)
