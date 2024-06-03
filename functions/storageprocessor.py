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
import statistics
import random
from matplotlib.lines import Line2D
import time

def remove_dir(directory):
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            time.sleep(2)
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

def create_dag(edges):
    G = nx.DiGraph()
    for edge in edges:
        source = edge['source']
        target = edge['target']
        G.add_edge(source, target)
    
    
    nodes = G.__dict__['_node']
    for node in nodes:
        command = ' '.join([label_part for label_part in node.label.split(' ') if '__aff_eloop__' not in label_part and '__aff_iloop__' not in label_part])

        nodes[node]['command'] = command

    return G

def save_dag(dag):
    node_mapping = {
        node: node.label for node in dag.nodes
    }

    # Relabel nodes with clearer labels
    dag_shortened = nx.relabel_nodes(dag, node_mapping)
    plt.figure(figsize=(14, 10))
    pos = custom_layout(dag_shortened)
    
    node_size = 6000
    node_color = "white"
    font_size = 10
    nx.draw(dag_shortened, pos, with_labels=True, node_size=node_size, node_color=node_color, font_size=font_size, font_weight='bold')
    
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Nodes', markerfacecolor='#1f78b4', markersize=10)
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    plt.show()

def custom_layout(dag):
    pos = {}
    y_positions = {}
    x_positions = {}
    already_assigned_position = set()
    previous_same_nodes = set()

    for node in nx.topological_sort(dag):
        preds = list(dag.predecessors(node))
        same_flag, same_nodes = one_preds_with_sync(node, preds, dag)
        if len(preds) == 0:
            xx = 0
            yy = 0
        else:
            if same_flag:
                pred_node_positions = [pos[pred_node] for pred_node in preds]
                average_coordinate = tuple(sum(coord[i] for coord in pred_node_positions) / len(pred_node_positions) for i in range(len(pred_node_positions[0])))

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

                yy = average_coordinate[1] + picked_value
                xx = average_coordinate[0] + 2
            elif len(preds) > 1:                
                xx = max(x_positions.values()) + 2
                pred_poses = []
                for pred_node in preds:
                    pred_poses.append(pos[pred_node])

                yy = statistics.mean([pred_pose[1] for pred_pose in pred_poses])
            elif len(preds) == 1:
                pred_node = preds[0]
                pred_node_position = pos[pred_node]

                xx = pred_node_position[0] + 2
                yy = pred_node_position[1]
              
        y_positions[node] = yy
        x_positions[node] = xx
        pos[node] = (xx, yy)
    
    return pos



