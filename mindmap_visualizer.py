import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

def visualize_mindmap(nodes, edges):
    """Visualize the keyword mindmap using streamlit-agraph."""
    
    # Configure the graph visualization with improved settings for mindmap display
    config = Config(
        width=1000,
        height=800,
        directed=True,
        physics=True,
        hierarchical=True,
        hierarchicalEnabled=True,
        hierarchicalLayout={
            "levelSeparation": 150,
            "nodeSpacing": 200,
            "treeSpacing": 200,
            "direction": "UD",  # Up to Down layout
            "sortMethod": "directed"  # Maintain parent-child relationships
        },
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",
        collapsible=True,
        node={
            "labelProperty": "label",
            "fontSize": 16,
            "fontWeight": "bold",
            "borderWidth": 2
        },
        link={
            "labelProperty": "label", 
            "renderLabel": False,
            "color": "#999999",
            "width": 2
        }
    )
    
    # Render the graph with custom title
    st.markdown("#### 🔍 Interactive Keyword Mindmap")
    st.markdown("*Hover over nodes to see details. Drag nodes to rearrange. Scroll to zoom.*")
    return agraph(nodes=nodes, edges=edges, config=config)

def get_intent_color(intent):
    """Get color based on intent category."""
    if intent == "Commercial":
        return "#4CAF50"  # Green
    elif intent == "Informational":
        return "#2196F3"  # Blue
    else:  # Navigational
        return "#FFC107"  # Yellow
