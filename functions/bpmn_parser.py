from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.bpmn.importer.variants.lxml import parse_element, Counts
from pm4py.objects.bpmn.importer import importer as bpmn_importer
from lxml import etree, objectify
import random


def extract_bpmn_information(bpmn_file):
    bpmn_graph = bpmn_importer.apply(bpmn_file)
    parser = etree.XMLParser(remove_comments=True)
    xml_tree = objectify.parse(bpmn_file, parser=parser)

    counts = Counts()
    curr_el = xml_tree.getroot()
    parents = []
    incoming_dict = {}
    outgoing_dict = {}
    flows_name = {}
    nodes_dict = {}
    nodes_bounds = {}
    flow_info = {}
    data_object_ref_dict = {}
    bpmn_graph = parse_element(bpmn_graph, counts, curr_el, parents, incoming_dict, outgoing_dict, flows_name, nodes_dict, nodes_bounds,
                    flow_info, data_object_ref_dict)
    
    return bpmn_graph

def find_rep_flows(bpmn_info):
    rep_flows = {}
    for flow_id, flow_details in bpmn_info["_BPMN__flows_details"].items():
        if flow_details["name"].startswith("rep:"):
            range_str = flow_details["name"][4:]  # Extracting the range string, e.g., "1:2"
            range_values = range_str.strip("[]").split(":")  # Splitting the range into start and end values
            start_value = int(range_values[0])
            end_value = int(range_values[1])
            random_value = random.randint(start_value, end_value)  # Generating a random number within the range

            # Retrieving source and target nodes for the flow
            source_node = flow_details["source_ref"]
            target_node = flow_details["target_ref"]

            rep_flows[flow_id] = {
                "random_value": random_value,
                "source_node": source_node,
                "target_node": target_node
            }

    return rep_flows 

def process_explicit_loops(bpmn_graph):
    bpmn_info = bpmn_graph.__dict__
    rep_flows_info = find_rep_flows(bpmn_info)
    _BPMN__node_annotations = bpmn_info['_BPMN__node_annotations']
    affected_nodes_to_remove = set()

    affected_flows = []
    for rep_flow_id, rep_flow_details in rep_flows_info.items():
        affected_nodes_to_remove.add(rep_flow_details["target_node"])
        affected_nodes_to_remove.add(rep_flow_details["source_node"])
        for flow_id, flow_details in bpmn_info["_BPMN__flows_details"].items():
            if flow_details["source_ref"] == rep_flow_details["target_node"]:
                activity_with_loop = flow_details["target_ref"]
                
            if (flow_details["source_ref"] == rep_flow_details["target_node"] or
                flow_details["target_ref"] == rep_flow_details["target_node"] or
                flow_details["source_ref"] == rep_flow_details["source_node"] or
                flow_details["target_ref"] == rep_flow_details["source_node"]):
                affected_flows.append(flow_details)
                
            if (flow_details["source_ref"] == rep_flow_details["source_node"] and
                flow_id != rep_flow_id):
                the_target_node = flow_details["target_ref"]
                
            if (flow_details["target_ref"] == rep_flow_details["target_node"] and
                flow_id != rep_flow_id):
                the_source_node = flow_details["source_ref"]
                
                
        new_activities = list()
        new_activities.append(activity_with_loop)
        for i in range(1, rep_flow_details["random_value"]):
            # base_name, application_label = str(activity_with_loop).split('@')
            # base_app, extension= application_label.split(".")
            # new_activity_name = f"{base_name}___explicit_loop___@{base_app}{i}.{extension}" if extension else f"{base_name}___explicit_loop___@{base_app}{i}"
            new_activity_name = activity_with_loop.name
            new_activity = BPMN.Task(name=new_activity_name)
            bpmn_graph.add_node(new_activity)
            bpmn_graph.add_node_annotation(new_activity, _BPMN__node_annotations[activity_with_loop])
            new_activities.append(new_activity)

    affected_flows_to_remove = set()
    for flow in bpmn_info['_BPMN__flows']:
        for a_flow in affected_flows:
            if (flow.source == a_flow["source_ref"] and 
                flow.target == a_flow["target_ref"]):
                affected_flows_to_remove.add(flow)
            else:
                pass

    for r_flow in affected_flows_to_remove:
        bpmn_graph.remove_flow(r_flow)

    new_flows = []
    new_flows.append((the_source_node, new_activities[0]))
    for i in range(len(new_activities) - 1):
        new_flows.append((new_activities[i], new_activities[i + 1]))
    new_flows.append((new_activities[-1], the_target_node))

    for n_flow in new_flows:
        flow_tuple = BPMN.Flow(n_flow[0], n_flow[1])
        bpmn_graph.add_flow(flow_tuple)

    for a_node in affected_nodes_to_remove:
        bpmn_graph.remove_node(a_node)

    return bpmn_graph

# def process_split_exclusive_gateway(parsed_bpmn):
#     bpmn_graph_obj = parsed_bpmn.__dict__
#     nodes = bpmn_graph_obj['_BPMN__nodes']
#     removed_nodes = set()
#     for node in nodes.copy():
#         if isinstance(node, BPMN.ExclusiveGateway):
#             if node.infer_direction() == "Spliting" or node.infer_direction() == None:
#                 removed_nodes.add(node)
#     flows = bpmn_graph_obj['_BPMN__flows']
#     flows_details = bpmn_graph_obj['_BPMN__flows_details']
#     node_annotations = bpmn_graph_obj['_BPMN__node_annotations']
#     removed_s_t_dict = dict()
#     for r_node in removed_nodes:
#         target_nodes = set()
#         source_nodes = set()
#         for flow in flows.copy():
#             if flow.source == r_node or flow.target == r_node:
#                 if flow.target == r_node:
#                     source_nodes.add(flow.source)
#                 else:
#                     target_nodes.add(flow.target)
#                 parsed_bpmn.remove_flow(flow)

#             removed_s_t_dict[r_node] = {
#                 "source": source_nodes,
#                 "target": target_nodes
#             }
#     for r_flow in removed_s_t_dict:
#         r_f_content = removed_s_t_dict[r_flow]
#         for r_flow_s in r_f_content['source']:
#             for r_flow_t in r_f_content['target']:
#                 new_node_name = str(str(r_flow_s).split('@')[1] + "___ghost___" + str(r_flow_t).split('@')[1])
#                 new_node = BPMN.Task(name=new_node_name)
#                 new_node_annotations = list()
#                 parsed_bpmn.add_node(new_node)
#                 in_flow = BPMN.Flow(r_flow_s, new_node)
#                 parsed_bpmn.add_flow(in_flow)
#                 out_flow = BPMN.Flow(new_node, r_flow_t)
#                 parsed_bpmn.add_flow(out_flow)

#                 for flow_detail in flows_details:
#                     details = flows_details[flow_detail]
#                     if r_flow == details['source_ref'] and r_flow_t == details['target_ref']:
#                         new_node_annotations.append(details['name'])
                
#                 node_annotations[str(new_node)] = new_node_annotations
#     for node in removed_nodes:
#         parsed_bpmn.remove_node(node)


#     annotations = bpmn_graph_obj['_BPMN__annotations']

# def process_split_parallel_gateway(parsed_bpmn):
#     bpmn_graph_obj = parsed_bpmn.__dict__
#     nodes = bpmn_graph_obj['_BPMN__nodes']

#     removed_nodes = set()
#     for node in nodes.copy():
#         if isinstance(node, BPMN.ParallelGateway):
#             if node.infer_direction() == "Spliting" or node.infer_direction() == None:
#                 removed_nodes.add(node)

#     flows = bpmn_graph_obj['_BPMN__flows']
#     removed_s_t_dict = dict()
#     for r_node in removed_nodes:
#         source_nodes = set()
#         target_nodes = set()
#         for flow in flows.copy():
#             if flow.source == r_node or flow.target == r_node:
#                 if flow.target == r_node:
#                     source_nodes.add(flow.source)
#                 else:
#                     target_nodes.add(flow.target)
#                 parsed_bpmn.remove_flow(flow)

#         removed_s_t_dict[r_node] = {
#             "source": source_nodes,
#             "target": target_nodes
#         }

#     for r_flow in removed_s_t_dict:
#         r_f_content = removed_s_t_dict[r_flow]
#         for r_flow_s in r_f_content['source']:
#             for r_flow_t in r_f_content['target']:
#                 a_flow = BPMN.Flow(r_flow_s, r_flow_t)
#                 parsed_bpmn.add_flow(a_flow)

#     for node in removed_nodes:
#         parsed_bpmn.remove_node(node)

# def process_join_parallel_gateway(parsed_bpmn, script_folder_name):
#     bpmn_graph_obj = parsed_bpmn.__dict__
#     nodes = bpmn_graph_obj['_BPMN__nodes']
#     node_flow_groups = bpmn_graph_obj['node_flow_groups']
#     flows = bpmn_graph_obj['_BPMN__flows']
#     flows_details = bpmn_graph_obj['_BPMN__flows_details']
#     node_annotations = bpmn_graph_obj['_BPMN__node_annotations']

#     removed_nodes = set()
#     for node in nodes.copy():
#         if isinstance(node, BPMN.ParallelGateway):
#             if node.infer_direction() == "Joining" or node.infer_direction() == None:
#                 removed_nodes.add(node)

#     removed_s_t_dict = dict()
#     for r_node in removed_nodes:
#         source_nodes = set()
#         target_nodes = set()
#         for flow in flows.copy():
#             if flow.source == r_node or flow.target == r_node:
#                 if flow.target == r_node:
#                     source_nodes.add(flow.source)
#                 else:
#                     target_nodes.add(flow.target)
#                 parsed_bpmn.remove_flow(flow)

#         removed_s_t_dict[r_node] = {
#             "source": source_nodes,
#             "target": target_nodes
#         }

#     for r_flow in removed_s_t_dict:
#         r_f_content = removed_s_t_dict[r_flow]
#         new_node_name = '___fake___'
#         new_node = BPMN.Task(name=new_node_name)
#         new_node_annotations = list()
#         parsed_bpmn.add_node(new_node)
#         for r_flow_s in r_f_content['source']:
#             in_flow = BPMN.Flow(r_flow_s, new_node)
#             parsed_bpmn.add_flow(in_flow)
        
#         for r_flow_t in r_f_content['target']:
#             out_flow = BPMN.Flow(new_node, r_flow_t)
#             parsed_bpmn.add_flow(out_flow)

#         node_flow_groups[str(new_node)] = 'and'
        
#         new_node_annotations.append('srun_command:{0}/{1}.py'.format(script_folder_name, new_node_name))    
#         node_annotations[str(new_node)] = new_node_annotations

#     for node in removed_nodes:
#         parsed_bpmn.remove_node(node)

# def process_join_exclusive_gateway(parsed_bpmn):
#     bpmn_graph_obj = parsed_bpmn.__dict__
#     nodes = bpmn_graph_obj['_BPMN__nodes']
#     node_flow_groups = bpmn_graph_obj['node_flow_groups']

#     removed_nodes = set()
#     for node in nodes.copy():
#         if isinstance(node, BPMN.ExclusiveGateway):
#             if node.infer_direction() == "Joining" or node.infer_direction() == None:
#                 removed_nodes.add(node)

#     flows = bpmn_graph_obj['_BPMN__flows']
#     removed_s_t_dict = dict()
#     for r_node in removed_nodes:
#         source_nodes = set()
#         target_nodes = set()
#         for flow in flows.copy():
#             if flow.source == r_node or flow.target == r_node:
#                 if flow.target == r_node:
#                     source_nodes.add(flow.source)
#                 else:
#                     target_nodes.add(flow.target)
#                 parsed_bpmn.remove_flow(flow)

#         removed_s_t_dict[r_node] = {
#             "source": source_nodes,
#             "target": target_nodes
#         }

#     related_arcs = list()
#     for r_flow in removed_s_t_dict:
#         r_f_content = removed_s_t_dict[r_flow]
#         for r_flow_t in r_f_content['target']:
#             for r_flow_s in r_f_content['source']:
#                 a_flow = BPMN.Flow(r_flow_s, r_flow_t)
#                 node_flow_groups[str(r_flow_t)] = 'or'
#                 related_arcs.append(a_flow)
#                 parsed_bpmn.add_flow(a_flow)

#     for node in removed_nodes:
#         parsed_bpmn.remove_node(node)

# def add_srun_filenames(parsed_bpmn):
#     bpmn_graph_obj = parsed_bpmn.__dict__
#     node_annotations = bpmn_graph_obj['_BPMN__node_annotations']
#     for node in node_annotations:
#         srun_filename = node.replace(' ', '_')
#         node_annotations[node].append('srun_filename:{}'.format(srun_filename))

# def pre_process_bpmn_file(parsed_bpmn, script_folder_name):
#     bpmn_graph_obj = parsed_bpmn.__dict__
#     bpmn_graph_obj['node_flow_groups'] = dict()
#     process_split_parallel_gateway(parsed_bpmn)
#     process_join_parallel_gateway(parsed_bpmn, script_folder_name)
#     process_split_exclusive_gateway(parsed_bpmn)
#     process_join_exclusive_gateway(parsed_bpmn)
#     add_srun_filenames(parsed_bpmn)
#     processed_bpmn = parsed_bpmn.__dict__
    
#     return processed_bpmn





