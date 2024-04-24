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

import hashlib
import statistics
import random

# def generate_hash(input_str):
#     hash_object = hashlib.md5(input_str.encode())
#     hex_digest = hash_object.hexdigest()
#     hash_4_digits = hex_digest[:4]
#     return hash_4_digits

def remove_dir(directory):
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            # print(f"Directory '{directory}' removed successfully.")
    except OSError as e:
        print(f"Error removing directory '{directory}': {e}")

def save_file(file, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = secure_filename(file.filename)
    file_path = os.path.join(directory, filename)
    file.save(file_path)

    return file_path

# def save_dag(dag):
#     # Create a mapping for nodes with clearer labels
#     node_mapping = {node: str(generate_hash(node.id)) + " " + node.name for node in dag.nodes}
    
#     # Relabel nodes with clearer labels
#     dag_shortened = nx.relabel_nodes(dag, node_mapping)
    
#     # Draw the graph with improved appearance
#     plt.figure(figsize=(10, 8))  # Set the figure size
#     nx.draw(dag_shortened, with_labels=True, node_size=800, node_color="skyblue", font_size=12, font_weight="bold", edge_color="gray", linewidths=0.5)
    
#     # Save the graph as an image
#     plt.savefig("dag_image.png", format="PNG", dpi=300, bbox_inches="tight")
    
#     # Display the graph
#     plt.show()

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import hashlib

def generate_hash(input_str):
    # Using MD5 hashing algorithm
    hash_object = hashlib.md5(input_str.encode())
    # Get the hexadecimal digest
    hex_digest = hash_object.hexdigest()
    # Take the first 4 characters
    hash_4_digits = hex_digest[:4]
    return hash_4_digits

def one_preds_with_sync(node, preds, dag):
    same_flag = False
    same_nodes = set()
    for new_node in nx.topological_sort(dag):
        if new_node != node:
            new_preds = list(dag.predecessors(new_node))
            if new_preds == preds:
                same_nodes.add(new_node)
                same_flag = True

    return same_flag, same_nodes    

def pick_and_remove_random(lst):
    # Pick a random element from the list
    random_element = random.choice(lst)
    # Remove the element from the list
    lst.remove(random_element)
    # Return the picked element
    return random_element


def custom_layout(dag):
    pos = {}
    y_positions = {}
    x_positions = {}
    already_assigned_position = set()
    for node in nx.topological_sort(dag):
        preds = list(dag.predecessors(node))

        if len(preds) == 0:
            xx = 0
            yy = 0
        elif len(preds) == 1:
            same_flag, same_nodes = one_preds_with_sync(node, preds, dag)
            if same_flag:
                pred_node = preds[0]
                pred_node_position = pos[pred_node]
                
                number = len(same_nodes) + 1
                if number%2 != 0:
                    my_list = list(range(-(int(number/2)), 0)) + list(range(0, (int(number/2)) + 1))
                else:
                    my_list = list(range(-int(number/2), 0)) + list(range(1, int(number/2) + 1))
                
                picked_value = random.choice(my_list)
                while picked_value in already_assigned_position:
                    picked_value = random.choice(my_list)
  
                already_assigned_position.add(picked_value)
                
                yy = pred_node_position[1] + picked_value
                xx = pred_node_position[0] + 1
                
            else:
                pred_node = preds[0]
                pred_node_position = pos[pred_node]

                xx = pred_node_position[0] + 1
                yy = pred_node_position[1]
                
        elif len(preds) > 1:
            same_flag, same_nodes = one_preds_with_sync(node, preds, dag)
            if same_flag:
                print("TODO")
            else:
                xx = max(x_positions.values()) + 1
                pred_poses = []
                for pred_node in preds:
                    pred_poses.append(pos[pred_node])

                yy = statistics.mean([pred_pose[1] for pred_pose in pred_poses])
        
        y_positions[node] = yy
        x_positions[node] = xx
        pos[node] = (xx, yy)
    
    return pos

def find_y_position(dag, already_processed, preds, pos):
    new_y_pos = 0
    number_of_preds = 0
    if len(preds) == 1:
        pre_pos = pos[preds[0]]
        new_y_pos = pre_pos[1]
        number_of_preds = 1
    elif len(preds) > 1:
        same_preds_list = []
        number_of_preds = 2
        for already_processed_node in already_processed:
            already_processed_preds = list(dag.predecessors(already_processed_node))
            if already_processed_preds == preds:
                
                pre_pos = pos[already_processed_node]
                same_preds_list.append(pre_pos)
            else:
                continue

        new_y_pos = -1 * statistics.mean([pred_pose[1] for pred_pose in same_preds_list])

            
    return number_of_preds, new_y_pos


def save_dag(dag):
    # Create a mapping for nodes with clearer labels
    annotations = dag._node
    node_mapping = {node: ("" if not annotations[node] else str(annotations[node]['annotations']) + " ") + str(generate_hash(node.id)) + " " + node.name for node in dag.nodes}
    
    # Relabel nodes with clearer labels
    dag_shortened = nx.relabel_nodes(dag, node_mapping)
    
    # Draw the graph with improved appearance
    plt.figure(figsize=(12, 8))  # Set the figure size
    
    # Define node positions with custom layout
    pos = custom_layout(dag_shortened)
    
    # Draw nodes with different colors and sizes
    node_size = 3500
    nx.draw_networkx_nodes(dag_shortened, pos, node_size=node_size, node_color="#1f78b4")
    
    # Draw node labels
    font_size = 10
    nx.draw_networkx_labels(dag_shortened, pos, font_size=font_size, font_weight="bold")
    
    # Draw edges with different styles
    nx.draw_networkx_edges(dag_shortened, pos, width=1.0, alpha=0.7, edge_color="black")
    
    # Add legend for node colors
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Nodes', markerfacecolor='#1f78b4', markersize=10)
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    # Save the graph as an image
    plt.savefig("dag_image.png", format="PNG", dpi=300, bbox_inches="tight")
    
    # Display the graph
    plt.show()




