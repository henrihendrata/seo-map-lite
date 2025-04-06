from streamlit_agraph import Node, Edge
import re
import uuid

def clean_id(text):
    """Clean text to be used as a node ID."""
    return re.sub(r'[^a-zA-Z0-9]', '_', text)

def process_data_for_visualization(keyword_data):
    """
    Process the keyword data structure to create nodes and edges for visualization.
    
    Args:
        keyword_data: The keyword structure dictionary
        
    Returns:
        Tuple of (nodes, edges) for agraph visualization
    """
    nodes = []
    edges = []
    
    # Keep track of used IDs
    used_ids = set()
    
    # Process the data to create nodes and edges
    def process_node(node, parent_id=None, depth=0):
        # Create a base ID for this node
        base_id = clean_id(node["keyword"])
        
        # Ensure uniqueness by adding a counter if needed
        node_id = base_id
        counter = 1
        
        # If the ID already exists in our set, add a unique suffix
        while node_id in used_ids:
            node_id = f"{base_id}_{counter}"
            counter += 1
            
        # Add this ID to our tracking set
        used_ids.add(node_id)
        
        # Get color based on intent
        if node["intent"] == "Commercial":
            color = "#4CAF50"  # Green
        elif node["intent"] == "Informational":
            color = "#2196F3"  # Blue
        else:  # Navigational
            color = "#FFC107"  # Yellow
        
        # Adjust size based on depth (root is largest)
        size = 15 if depth == 0 else (12 if depth == 1 else 10)
        
        # Create node with tooltip containing additional info
        tooltip = (
            f"Intent: {node['intent']}\n"
            f"Word Count: {node['word_count']}\n"
            f"Title: {node['title']}"
        )
        
        # Add competitors to tooltip if available
        if node.get("competitors") and len(node["competitors"]) > 0:
            tooltip += "\n\nTop Competitors:"
            for comp in node["competitors"][:3]:
                tooltip += f"\n• {comp.get('title', 'Unknown')}"
        
        # Add node to list
        nodes.append(Node(
            id=node_id,
            label=node["keyword"],
            size=size,
            color=color,
            title=tooltip
        ))
        
        # If this node has a parent, create an edge
        if parent_id:
            edges.append(Edge(source=parent_id, target=node_id))
        
        # Process child nodes
        for child in node["children"]:
            process_node(child, node_id, depth + 1)
    
    # Start processing from the root node
    process_node(keyword_data)
    
    return nodes, edges
