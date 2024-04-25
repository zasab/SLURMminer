import sys, os
from os.path import dirname, abspath
filedir = dirname(abspath(__file__))
basedir = dirname(dirname(abspath(__file__)))
sys.path.insert(1, basedir)
from werkzeug.utils import secure_filename
import shutil
import matplotlib.pyplot as plt
import networkx as nx
from pm4py.objects.bpmn.obj import BPMN

import os
from werkzeug.utils import secure_filename

import hashlib
import statistics
import random
from matplotlib.lines import Line2D

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



def generate_hash(input_str):
    hash_object = hashlib.md5(input_str.encode())
    hex_digest = hash_object.hexdigest()
    hash_3_digits = hex_digest[:3]
    return hash_3_digits

def one_preds_with_sync(node, preds, dag):
    same_flag = False
    same_nodes = set()
    same_nodes.add(node)
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
    previous_same_nodes = set()

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
                
                number = len(same_nodes)
                if number%2 != 0:
                    my_list = list(range(-(int(number/2)), 0)) + list(range(0, (int(number/2)) + 1))
                else:
                    my_list = list(range(-int(number/2), 0)) + list(range(1, int(number/2) + 1))

                if same_nodes != previous_same_nodes:
                    already_assigned_position = set()
                    previous_same_nodes = same_nodes
                
                picked_value = random.choice(my_list)
                while picked_value in already_assigned_position:
                    picked_value = random.choice(my_list)
  
                already_assigned_position.add(picked_value)
                
                yy = pred_node_position[1] + picked_value
                xx = pred_node_position[0] + 2
                
            else:
                pred_node = preds[0]
                pred_node_position = pos[pred_node]

                xx = pred_node_position[0] + 2
                yy = pred_node_position[1]
                
        elif len(preds) > 1:
            same_flag, same_nodes = one_preds_with_sync(node, preds, dag)
            if same_flag:
                print("TODO")
            else:                
                xx = max(x_positions.values()) + 2
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
    annotations = dag._node
    node_mapping = {
        node: (
            (("XOR " if isinstance(node, BPMN.ExclusiveGateway) else
            "AND " if isinstance(node, BPMN.ParallelGateway) else
            "END " if isinstance(node, BPMN.NormalEndEvent) else
            "START " if isinstance(node, BPMN.NormalStartEvent) else
            "") +
            ("" if not annotations[node] else str(annotations[node]['annotations'][0]) + "__") +
            str(generate_hash(f"{node.id}_{type(node).__name__}")) + " " +
            node.name)
        ) for node in dag.nodes
    }
    # Relabel nodes with clearer labels
    dag_shortened = nx.relabel_nodes(dag, node_mapping)
    
    # Draw the graph with improved appearance
    plt.figure(figsize=(14, 10))  # Set the figure size
    
    # Define node positions with custom layout
    pos = custom_layout(dag_shortened)
    
    # Draw nodes with different colors and sizes
    node_size = 4500
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




