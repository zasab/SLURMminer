from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.bpmn.importer.variants.lxml import parse_element, Counts
from pm4py.objects.bpmn.importer import importer as bpmn_importer
from lxml import etree, objectify
import random
from functions import BpmnUtils

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

def pre_processing(bpmn_graph):
    bpmn_info = bpmn_graph.__dict__
    new_flows_set = set()
    flows = bpmn_info['_BPMN__flows']
    flows_to_remove = set()

    for flow in flows:
        flow_tuple = (flow.source, flow.target)
        if flow_tuple not in new_flows_set:
            new_flows_set.add(flow_tuple)
        flows_to_remove.add(flow)

    for flow in flows_to_remove:
        bpmn_graph.remove_flow(flow)
    
    for n_flow in new_flows_set:
        bpmn_flow = BPMN.SequenceFlow(n_flow[0], n_flow[1])
        bpmn_graph.add_flow(bpmn_flow)

    return bpmn_graph

def add_activity(bpmn_graph, name, annotation):
    new_activity = BPMN.Task(name=name)
    bpmn_graph.add_node(new_activity)
    bpmn_graph.add_node_annotation(new_activity, annotation)

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

    if len(rep_flows_info) == 0:
        pass
    else:
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
            flow_tuple = BPMN.SequenceFlow(n_flow[0], n_flow[1])
            bpmn_graph.add_flow(flow_tuple)

        for a_node in affected_nodes_to_remove:
            bpmn_graph.remove_node(a_node)

    return bpmn_graph

def find_hidden_loops(bpmn_info):
    hidden_flows = {}
    for flow_id, flow_details in bpmn_info["_BPMN__flows_details"].items():
        if (flow_details["name"] and not flow_details["name"].startswith("rep:")):
            hidden_flows[flow_id] = {
                "iterative_attribute": flow_details["name"],
                "source_node": flow_details["source_ref"],
                "target_node": flow_details["target_ref"]
            }

    return hidden_flows

def process_iterative_flow_details(flows, hidden_flow_details, _BPMN__node_annotations):
    iterative_attribute = hidden_flow_details['iterative_attribute']
    start_of_loop = hidden_flow_details['target_node']
    end_of_loop = hidden_flow_details['source_node']

    nodes_affected_from_iteration = set()
    needs_processed_again_flows = set()
    incomings = set()
    outgoings = set()

    for flow0 in flows:
        if flow0.target == start_of_loop and flow0.source != end_of_loop:
            incomings.add(flow0.source)
        elif flow0.source == end_of_loop and flow0.target != start_of_loop:
            outgoings.add(flow0.target)
        else:
            pass

    for flow in flows:
        if flow.source == start_of_loop:
            activity_with_iteration = flow.target
            nodes_affected_from_iteration.add(activity_with_iteration)
            iteration_info = _BPMN__node_annotations[activity_with_iteration]
            iteration_info_dict = {}
            for iter in iteration_info:
                iter_value = iter.__dict__['_TextAnnotation__command']
                parameter_id, values_list = BpmnUtils.parameter_string_to_dict(iter_value)
                iteration_info_dict[parameter_id]= values_list
        elif flow.target == end_of_loop:
            nodes_affected_from_iteration.add(flow.source)
        elif flow.target in nodes_affected_from_iteration:
            nodes_affected_from_iteration.add(flow.source)
        elif flow.source in nodes_affected_from_iteration:
            nodes_affected_from_iteration.add(flow.target)
        else:
            needs_processed_again_flows.add(flow)
            continue

    for flow2 in needs_processed_again_flows:
        if flow2.source == start_of_loop:
            activity_with_iteration = flow2.target
            nodes_affected_from_iteration.add(activity_with_iteration)
            iteration_info = _BPMN__node_annotations[activity_with_iteration]
            iteration_info_dict = {}
            for iter in iteration_info:
                iter_value = iter.__dict__['_TextAnnotation__command']
                parameter_id, values_list = BpmnUtils.parameter_string_to_dict(iter_value)
                iteration_info_dict[parameter_id]= values_list
        elif flow2.target == end_of_loop:
            nodes_affected_from_iteration.add(flow2.source)
        elif flow2.target in nodes_affected_from_iteration:
            nodes_affected_from_iteration.add(flow2.source)
        elif flow2.source in nodes_affected_from_iteration:
            nodes_affected_from_iteration.add(flow2.target)
        else:
            if flow2 not in needs_processed_again_flows:
                needs_processed_again_flows.add(flow2)
            continue

    return start_of_loop, activity_with_iteration, BpmnUtils.generate_combinations(iteration_info_dict), end_of_loop, incomings, outgoings


def process_hidden_loops(bpmn_graph):
    bpmn_info = bpmn_graph.__dict__
    nodes = bpmn_info['_BPMN__nodes']
    flows = bpmn_info['_BPMN__flows']

    _BPMN__node_annotations = bpmn_info['_BPMN__node_annotations']
    hidden_flows = find_hidden_loops(bpmn_info)
    
    for hidden_flow_id, hidden_flow_details in hidden_flows.items():
        start_of_loop, activity_with_iteration, combinations, end_of_loop, incomings, outgoings = process_iterative_flow_details(flows, hidden_flow_details, _BPMN__node_annotations)
        affected_flows_to_remove = set()
        affected_nodes_to_remove = set()
        all_new_activities = {}
        all_new_flows = set()
        correspondings = {}
        before_last_nodes = []

        affected_nodes_to_remove.add(start_of_loop)
        affected_nodes_to_remove.add(end_of_loop)
        new_start = BPMN.ParallelGateway(start_of_loop.id, name=start_of_loop.id)
        
        correspondings[start_of_loop] = {new_start}
        all_new_activities[new_start] = ""
        for in_node in incomings:
            in_flow = BPMN.SequenceFlow(in_node, new_start)
            all_new_flows.add(in_flow)

        new_end = BPMN.ParallelGateway(end_of_loop.id, name=end_of_loop.id)
        correspondings[end_of_loop] = {new_end}
        all_new_activities[new_end] = ""
        for out_node in outgoings:
            out_flow = BPMN.SequenceFlow(new_end, out_node)
            all_new_flows.add(out_flow)
        
        for com in combinations:
            con_str = [f"{key}:[{', '.join(value)}]" for key, value in com.items()]
            new_activity_name = activity_with_iteration.name
            new_activity = BPMN.Task(name=new_activity_name)
            if activity_with_iteration not in correspondings:
                correspondings[activity_with_iteration] = {new_activity}
            else:
                correspondings[activity_with_iteration].add(new_activity)

            all_new_activities[new_activity]=con_str
            new_start_flow = BPMN.SequenceFlow(new_start, new_activity)
            all_new_flows.add(new_start_flow)
            # bpmn_graph.add_node(new_activity)
            # bpmn_graph.add_node_annotation(new_activity, con_str)
            affected_nodes_to_remove.add(activity_with_iteration)
            replicate_sub_nodes(bpmn_graph, start_of_loop, {activity_with_iteration}, {new_activity}, flows, end_of_loop, new_end, all_new_activities, all_new_flows, affected_nodes_to_remove, affected_flows_to_remove, correspondings, before_last_nodes)
        
        
        before_last_nodes_corresponding = correspondings[before_last_nodes[0]]

        for before_last_node_corresponding in before_last_nodes_corresponding:
            before_last_node_flow = BPMN.SequenceFlow(before_last_node_corresponding, new_end)
            all_new_flows.add(before_last_node_flow)

        for node_id, annot in all_new_activities.items():
            bpmn_graph.add_node(node_id)
            if annot:
                bpmn_graph.add_node_annotation(node_id, annot)

        for neew_flow in all_new_flows:
            bpmn_graph.add_flow(neew_flow)

        for affected_node in affected_nodes_to_remove:
            bpmn_graph.remove_node(affected_node)

        for affected_flow in affected_flows_to_remove:
            bpmn_graph.remove_flow(affected_flow)

        return bpmn_graph
        
def replicate_sub_nodes(bpmn_graph, start_of_loop, current_activities, new_activities, flows, end, new_end, all_new_activities, all_new_flows, affected_nodes_to_remove, affected_flows_to_remove, correspondings, before_last_nodes):
    bpmn_obj = bpmn_graph.__dict__
    _BPMN__node_annotations = bpmn_obj['_BPMN__node_annotations']
    
    # Termination condition: Stop if end_of_loop is in current_nodes
    if end in current_activities:
        affected_nodes_to_remove.add(end)
        return
    
    target_nodes = set()
    source_nodes = set()

    for flow_i in flows.copy():
        if (flow_i.source == start_of_loop or
            flow_i.target == start_of_loop or
            flow_i.source == end or
            flow_i.target == end):
            affected_flows_to_remove.add(flow_i)

        if flow_i.source in current_activities:
            target_node = flow_i.target
            if target_node != end:
                target_nodes.add(target_node)
                target_new_node = BPMN.Task(name=target_node.name)
                if target_node not in correspondings:
                    correspondings[target_node] = {target_new_node}
                else:
                    correspondings[target_node].add(target_new_node)

                source_nodes.add(target_new_node)
                if target_node in _BPMN__node_annotations:
                    all_new_activities[target_new_node] = _BPMN__node_annotations[target_node]
                else:
                    all_new_activities[target_new_node] = ""
                # bpmn_graph.add_node(target_new_node)
                # if target_node in _BPMN__node_annotations:
                #     bpmn_graph.add_node_annotation(target_new_node, _BPMN__node_annotations[target_node])

                affected_nodes_to_remove.add(target_node)
                for n_activity in new_activities:
                    new_flow = BPMN.SequenceFlow(n_activity, target_new_node)
                    all_new_flows.add(new_flow)
                    # bpmn_graph.add_flow(out_flow)

                affected_flows_to_remove.add(flow_i)
            else:
                before_last_nodes.append(flow_i.source)
                
            #     new_flow = BPMN.Flow(n_activity, new_end)
            #     all_new_flows.add(new_flow)
    
    if target_nodes:
        replicate_sub_nodes(bpmn_graph, start_of_loop, target_nodes, source_nodes, flows, end, new_end, all_new_activities, all_new_flows, affected_nodes_to_remove, affected_flows_to_remove, correspondings, before_last_nodes)


def nested_node_generation(bpmn_graph, current_nodes, flows, affected_nodes_to_remove, end_of_loop):
    bpmn_obj = bpmn_graph.__dict__
    _BPMN__node_annotations = bpmn_obj['_BPMN__node_annotations']
    
    # Termination condition: Stop if end_of_loop is in current_nodes
    if end_of_loop in current_nodes:
        return
    
    target_nodes = set()  # Using set to store unique target nodes
    
    for flow_i in flows:
        for c_node in current_nodes:
            if flow_i.source == c_node:
                target_node = flow_i.target
                target_nodes.add(flow_i.target)
                target_new_node = BPMN.Task(name=target_node.name)
                bpmn_graph.add_node(target_new_node)
                if c_node in _BPMN__node_annotations:
                    bpmn_graph.add_node_annotation(target_new_node, _BPMN__node_annotations[c_node])
                affected_nodes_to_remove.add(c_node)
                

    if target_nodes:
        nested_node_generation(bpmn_graph, target_nodes, flows, affected_nodes_to_remove, end_of_loop)



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





