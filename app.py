import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit as st

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

# Create a combined graph
G_combined = nx.compose(G_supports, G_refutes)

# Use Pyvis to visualize the graph
def visualize_graph(graph, title):
    net = Network(height="800px", width="100%", directed=True)
    for node in graph.nodes(data=True):
        net.add_node(node[0], title=str(node[0]), label=str(node[0]))

    for edge in graph.edges(data=True):
        net.add_edge(edge[0], edge[1], value=edge[2].get('weight', 1))

    net.set_options("""
        var options = {
          "nodes": {
            "font": {
              "size": 14,
              "face": "arial"
            },
            "scaling": {
              "label": true
            }
          },
          "edges": {
            "arrows": {
              "to": {
                "enabled": true
              }
            },
            "color": {
              "inherit": true
            },
            "smooth": {
              "enabled": true
            }
          },
          "physics": {
            "enabled": true,
            "stabilization": {
              "enabled": true
            }
          }
        }
    """)
    net.show(title)

# Streamlit app layout
st.title("Interactive Network Graph")

# Sidebar for selecting graph type
graph_type = st.sidebar.selectbox(
    "Select Graph Type",
    ("Supports", "Refutes", "Combined")
)

if graph_type == "Supports":
    st.subheader("Graph: Supports")
    visualize_graph(G_supports, "Supports Network")

elif graph_type == "Refutes":
    st.subheader("Graph: Refutes")
    visualize_graph(G_refutes, "Refutes Network")

else:
    st.subheader("Graph: Combined")
    visualize_graph(G_combined, "Combined Network")
