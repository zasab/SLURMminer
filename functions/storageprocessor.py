import sys, os
from os.path import dirname, abspath
filedir = dirname(abspath(__file__))
basedir = dirname(dirname(abspath(__file__)))
sys.path.insert(1, basedir)
from werkzeug.utils import secure_filename
import shutil
import matplotlib.pyplot as plt
import networkx as nx

import os
from werkzeug.utils import secure_filename

def remove_dir(directory):
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"Directory '{directory}' removed successfully.")
    except OSError as e:
        print(f"Error removing directory '{directory}': {e}")

def save_file(file, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = secure_filename(file.filename)
    file_path = os.path.join(directory, filename)
    file.save(file_path)

    return file_path

def save_dag(dag):
    # Create a mapping for nodes with clearer labels
    node_mapping = {node: str(node).split("@")[-1] if str(node).split("@")[-1] else str(node).split("@")[0] for node in dag.nodes}
    
    # Relabel nodes with clearer labels
    dag_shortened = nx.relabel_nodes(dag, node_mapping)
    
    # Draw the graph with improved appearance
    plt.figure(figsize=(10, 8))  # Set the figure size
    nx.draw(dag_shortened, with_labels=True, node_size=800, node_color="skyblue", font_size=12, font_weight="bold", edge_color="gray", linewidths=0.5)
    
    # Save the graph as an image
    plt.savefig("dag_image.png", format="PNG", dpi=300, bbox_inches="tight")
    
    # Display the graph
    plt.show()


