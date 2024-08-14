from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.bpmn.importer.variants.lxml import parse_element, Counts
from pm4py.objects.bpmn.importer import importer as bpmn_importer
from lxml import etree, objectify
import random
from functions import BpmnUtils
from functions import storageprocessor
import string
import ast
from functions.graphObject import JOB
from functions import common_functions

random_strings = set()
def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

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
    
    for n_flow in new_flows_set:
        bpmn_flow = BPMN.SequenceFlow(n_flow[0], n_flow[1])
        bpmn_graph.add_flow(bpmn_flow)


    for a_flow in flows_to_remove:
        bpmn_graph.remove_flow(a_flow)

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

def process_single_value_arguments(bpmn_graph):
    bpmn_info = bpmn_graph.__dict__

    _BPMN__node_annotations = bpmn_info['_BPMN__node_annotations']
    _BPMN__flows = bpmn_info['_BPMN__flows']

    affected_nodes = set()
    affected_flows = set()
    new_nodes = set()
    new_flows = set()
    corresponding_nodes = {}
    corresponding1={}
    new_annotation_lists = {}
    for node, arguments in _BPMN__node_annotations.items():
        single_value_arguments_dict = {}
        new_arguments_list = []
        for argument in arguments:
            argument_str = str(argument)
            arg_parts = argument_str.split(':')
            value_list = ast.literal_eval(arg_parts[1])
            if len(value_list) == 1:
                single_value_arguments_dict[arg_parts[0]] = value_list[0]
            else:
                new_arguments_list.append(argument)

        if single_value_arguments_dict:
            node_parts = node.name.split()
            affected_nodes.add(node)
            for i in range(len(node_parts)):
                if node_parts[i].startswith('$'):
                    key = node_parts[i][1:]  # Extract key after '$'
                    if key in single_value_arguments_dict:
                        node_parts[i] = str(single_value_arguments_dict[key])

            new_node_command = ' '.join(node_parts)
            new_node = BPMN.Task(name=new_node_command)
            new_nodes.add(new_node)
            data_object_factory(bpmn_graph, new_node, node)
            job_id = 'job_id_' + str(common_functions.get_unique_number_added_to_job_id(new_node))
            JOB(task=new_node, job_id=job_id)
            JOB.set_corresponding_task_form_initial_bpmn_by_job_id(job_id, node)
            parent_job_id = JOB.get_job_id_by_task(node)
            if JOB.get_choice_flag_by_id(parent_job_id):
                JOB.set_choice_flag_by_id(job_id, True)

            new_annotation_lists[new_node] = new_arguments_list                
            corresponding_nodes[node] = new_node
            corresponding1[node]={new_node}
   
    for aa_node in affected_nodes:
        for flow in _BPMN__flows:
            if flow.source == aa_node:
                affected_flows.add(flow)
                if flow.target in corresponding_nodes:
                    new_flows.add((corresponding_nodes[aa_node], corresponding_nodes[flow.target]))
                else:
                    new_flows.add((corresponding_nodes[aa_node], flow.target))
            elif flow.target == aa_node:
                affected_flows.add(flow)
                if flow.source in corresponding_nodes:
                    new_flows.add((corresponding_nodes[flow.source], corresponding_nodes[aa_node]))
                else:
                    new_flows.add((flow.source, corresponding_nodes[aa_node]))
    
    for n_node in new_nodes:
        arg_list = new_annotation_lists[n_node]
        if arg_list:
            bpmn_graph.add_node_annotation(n_node, arg_list)
        bpmn_graph.add_node(n_node)

    for n_flow in new_flows:
        flow_obj = BPMN.SequenceFlow(n_flow[0], n_flow[1])
        bpmn_graph.add_flow(flow_obj)

    for a_flow in affected_flows:
        bpmn_graph.remove_flow(a_flow)

    for a_node in affected_nodes:
        bpmn_graph.remove_node(a_node)

    return bpmn_graph

def get_key_from_value(d, i_key):
    for key, val in d.items():
        if key == i_key:
            return val
    return None


def data_object_factory(bpmn_graph, new_node, old_node):
    _BPMN__data_objects= bpmn_graph.__dict__['_BPMN__data_objects']

    for key1, __data_object in list(_BPMN__data_objects.items()):
        source_ref = __data_object['source_ref']
        target_refs = __data_object['target_ref']
        

        if old_node == source_ref:
            bpmn_data_obj_1 = BPMN.DataObjectReference(name=__data_object['name'], 
                                                    process=None, sourceRef=new_node.id,
                                                    targetRef=target_refs)
            bpmn_graph.add_data_obj(bpmn_data_obj_1)
        
        if old_node in target_refs:
            bpmn_data_obj_2 = BPMN.DataObjectReference(name=__data_object['name'], 
                                                    process=None, sourceRef=source_ref,
                                                    targetRef=[new_node.id])
            bpmn_graph.add_data_obj(bpmn_data_obj_2)

def remove_nodes_through(bpmn_graph, affected_nodes):
    for old_node1 in affected_nodes:
        bpmn_graph.remove_node(old_node1)

    return bpmn_graph

def remove_flows_through(bpmn_graph, affected_flows):
    for a_flow in affected_flows:
        bpmn_graph.remove_flow(a_flow)

    return bpmn_graph

def process_explicit_loops(bpmn_graph):
    bpmn_info1 = bpmn_graph.__dict__
    rep_flows_info = find_rep_flows(bpmn_info1)

    if len(rep_flows_info) == 0:
        pass
    else:
        for rep_flow_id, rep_flow_details in rep_flows_info.items():
            bpmn_info = bpmn_graph.__dict__
            start_nodes = set()
            end_nodes = set()
            _BPMN__flows = bpmn_info['_BPMN__flows']
            _BPMN__node_annotations = bpmn_info['_BPMN__node_annotations']
            affected_nodes_to_remove = set()
            affected_flows = set()
            new_flows = set()
            new_activities = set()
            corresponding2 = {}

            rep_flow_source = rep_flow_details["source_node"]
            rep_flow_target = rep_flow_details["target_node"]
            rep_flow_random_value = rep_flow_details["random_value"]
            affected_nodes_to_remove.add(rep_flow_source)
            affected_nodes_to_remove.add(rep_flow_target)

            for flow in _BPMN__flows:
                flow_source = flow.source
                flow_target = flow.target

                if flow_source == rep_flow_target:
                    activity_with_loop = flow_target
                    affected_flows.add(flow)

                if flow_target == rep_flow_source:
                    affected_flows.add(flow)

                if flow_target == rep_flow_target:
                    if flow_source != rep_flow_source:
                        start_nodes.add(flow_source)
                    affected_flows.add(flow)                        
                if flow_source == rep_flow_source:
                    if flow_target != rep_flow_target:
                        end_nodes.add(flow_target)
                    affected_flows.add(flow)
            
            for start_node in start_nodes:
                flow_tuple = (start_node, activity_with_loop)
                new_flows.add(flow_tuple)
            
            previous_new_node = activity_with_loop
            for i in range(1, rep_flow_random_value):
                activity_with_loop_annot = ""
                if activity_with_loop in _BPMN__node_annotations:
                    activity_with_loop_annot = _BPMN__node_annotations[activity_with_loop]

                random_string1 = generate_random_string(3)
                while random_string1 in random_strings:
                    random_string1 = generate_random_string(3)
                new_activity_name = random_string1 + '__aff_eloop__' + activity_with_loop.name
                random_strings.add(random_string1) 

                new_activity = BPMN.Task(name=new_activity_name)
                data_object_factory(bpmn_graph, new_activity, activity_with_loop)
                job_id = 'job_id_' + str(common_functions.get_unique_number_added_to_job_id(new_activity))
                JOB(task= new_activity, job_id=job_id)
                JOB.set_corresponding_task_form_initial_bpmn_by_job_id(job_id, activity_with_loop)

                parent_job_id = JOB.get_job_id_by_task(activity_with_loop)
                if JOB.get_choice_flag_by_id(parent_job_id):
                    JOB.set_choice_flag_by_id(job_id, True)

                if activity_with_loop_annot:
                    bpmn_graph.add_node_annotation(new_activity, activity_with_loop_annot)
                
                if activity_with_loop not in corresponding2:
                    corresponding2[activity_with_loop] = {new_activity}
                else:
                    corresponding2[activity_with_loop].add(new_activity)

                new_activities.add(new_activity)

                if i == rep_flow_random_value -1:
                    flow_tuple4 = (previous_new_node, new_activity)
                    new_flows.add(flow_tuple4)
                    for end_node in end_nodes:
                        flow_tuple2 = (new_activity, end_node)
                        new_flows.add(flow_tuple2)
                else:
                    flow_tuple3 = (previous_new_node, new_activity)
                    previous_new_node = new_activity
                    new_flows.add(flow_tuple3)

            if rep_flow_random_value == 1:
                for end_node in end_nodes:
                    flow_tuple4 = (activity_with_loop, end_node)
                    new_flows.add(flow_tuple4)


            for n_activity in new_activities:
                bpmn_graph.add_node(n_activity)

            for new_flow in new_flows:
                flow_obj = BPMN.SequenceFlow(new_flow[0], new_flow[1])
                bpmn_graph.add_flow(flow_obj)

            for a_flow in affected_flows:
                bpmn_graph.remove_flow(a_flow)

    return bpmn_graph

def find_hidden_loops(bpmn_info):
    hidden_flows = {}
    for flow_id, flow_details in bpmn_info["_BPMN__flows_details"].items():
        if (flow_details["name"] 
            and not flow_details["name"].startswith("rep:")
            and not flow_details["name"].startswith("SLURM:")) :
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

    combinations = BpmnUtils.generate_combinations(iteration_info_dict)      
    return start_of_loop, activity_with_iteration, combinations, end_of_loop, incomings, outgoings

def connected_nodes(start, end, flows, __connected_nodes):
    for flow in flows:
        if flow.source == start:
            if flow.target != end:
                __connected_nodes.add(flow.target)
                connected_nodes(flow.target, end, flows, __connected_nodes)
        
    
    return __connected_nodes



def process_hidden_loops(bpmn_graph):
    bpmn_info = bpmn_graph.__dict__
    nodes = bpmn_info['_BPMN__nodes']
    flows = bpmn_info['_BPMN__flows']

    _BPMN__node_annotations = bpmn_info['_BPMN__node_annotations']
    hidden_flows = find_hidden_loops(bpmn_info)
    affected_nodes_to_remove = set()
    affected_flows_to_remove = set()
    correspondings3={}
    
    for hidden_flow_id, hidden_flow_details in hidden_flows.items():
        start_of_loop, activity_with_iteration, combinations, end_of_loop, incomings, outgoings = process_iterative_flow_details(flows, hidden_flow_details, _BPMN__node_annotations)
        
        affected_nodes_to_remove = set()
        affected_flows_to_remove = set()
        all_new_activities = {}
        all_new_flows = set()
        correspondings3 = {}
        before_last_nodes = []

        affected_nodes_to_remove.add(start_of_loop)
        affected_nodes_to_remove.add(end_of_loop)

        __connected_nodes = set()
        __connected_nodes = connected_nodes(start_of_loop, end_of_loop, flows, __connected_nodes)

        new_start_name = 'S_AND__' + common_functions.generate_unique_hash(str(start_of_loop.id))
        new_start = BPMN.ParallelGateway(name=new_start_name)
        
        correspondings3[start_of_loop] = {new_start}
        all_new_activities[new_start] = ""
        for in_node in incomings:
            new_tupplee1 = (in_node, new_start)
            # in_flow = BPMN.SequenceFlow(in_node, new_start)
            all_new_flows.add(new_tupplee1)

        new_end_name = 'E_AND__' + common_functions.generate_unique_hash(str(end_of_loop.id))
        new_end = BPMN.ParallelGateway(name=new_end_name)
        correspondings3[end_of_loop] = {new_end}
        all_new_activities[new_end] = ""
        for out_node in outgoings:
            new_tupplee2 = (new_end, out_node)
            # out_flow = BPMN.SequenceFlow(new_end, out_node)
            all_new_flows.add(new_tupplee2)
        
        for com in combinations:
            con_str = [f"{key}:[{', '.join(value)}]" for key, value in com.items()]

            new_activity_name = BpmnUtils.replace_placeholders(activity_with_iteration.name, com)
            new_activity = BPMN.Task(name=new_activity_name)

            data_object_factory(bpmn_graph, new_activity, activity_with_iteration)
            job_id = 'job_id_' + str(common_functions.get_unique_number_added_to_job_id(new_activity))
            JOB(task=new_activity, job_id=job_id)
            JOB.set_corresponding_task_form_initial_bpmn_by_job_id(job_id, activity_with_iteration)

            parent_job_id = JOB.get_job_id_by_task(activity_with_iteration)
            if JOB.get_choice_flag_by_id(parent_job_id):
                JOB.set_choice_flag_by_id(job_id, True)
            
            if activity_with_iteration not in correspondings3:
                correspondings3[activity_with_iteration] = {new_activity}
            else:
                correspondings3[activity_with_iteration].add(new_activity)

            all_new_activities[new_activity]=con_str
            new_tupplee3 = (new_start, new_activity)
            all_new_flows.add(new_tupplee3)
            affected_nodes_to_remove.add(activity_with_iteration)
            replicate_sub_nodes(bpmn_graph, start_of_loop, {activity_with_iteration}, {new_activity}, flows, end_of_loop, new_end, all_new_activities, all_new_flows, affected_nodes_to_remove, affected_flows_to_remove, correspondings3, before_last_nodes, __connected_nodes)
        
        before_last_nodes_corresponding = correspondings3[before_last_nodes[0]]

        for before_last_node_corresponding in before_last_nodes_corresponding:
            new_tupplee4 = (before_last_node_corresponding, new_end)
            # before_last_node_flow = BPMN.SequenceFlow(before_last_node_corresponding, new_end)
            all_new_flows.add(new_tupplee4)

        
        for node_id, annot in all_new_activities.items():
            bpmn_graph.add_node(node_id)
            if annot:
                bpmn_graph.add_node_annotation(node_id, annot)

        for neew_flow in all_new_flows:
            flow_obj = BPMN.SequenceFlow(neew_flow[0], neew_flow[1])
            bpmn_graph.add_flow(flow_obj)

        for a_flow in affected_flows_to_remove:
            bpmn_graph.remove_flow(a_flow)

        for a_node in affected_nodes_to_remove:
            bpmn_graph.remove_node(a_node)
    
    return bpmn_graph
        
def replicate_sub_nodes(bpmn_graph, start_of_loop, initial_activities_that_are_going_to_replicate, new_activities, flows, end, new_end, all_new_activities, 
                        all_new_flows, affected_nodes_to_remove, affected_flows_to_remove, correspondings3, before_last_nodes, __connected_nodes):
    bpmn_obj = bpmn_graph.__dict__
    _BPMN__node_annotations = bpmn_obj['_BPMN__node_annotations']
    
    if end in initial_activities_that_are_going_to_replicate:
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

        if flow_i.source in initial_activities_that_are_going_to_replicate:
            target_node = flow_i.target
            if target_node != end:
                target_nodes.add(target_node)

                random_string2 = generate_random_string(3)
                while random_string2 in random_strings:
                    random_string2 = generate_random_string(3)
                
                target_new_node_name = random_string2 + '__aff_iloop__' + target_node.name
                
                __input_nodes = return_input_nodes_in_BPMN(target_node, flows)
                __excluded_input_nodes = set()
                #TODO __excluded_output_nodes
                for __input_node in __input_nodes:
                    if __input_node not in __connected_nodes:
                        __excluded_input_nodes.add(__input_node)
                if isinstance(target_node, BPMN.ParallelGateway):
                    target_new_node = BPMN.ParallelGateway(name=target_new_node_name)
                    
                elif isinstance(target_node, BPMN.ExclusiveGateway):
                    target_new_node = BPMN.ExclusiveGateway(name=target_new_node_name)
                else:
                    target_new_node = BPMN.Task(name=target_new_node_name)
                    data_object_factory(bpmn_graph, target_new_node, target_node)
                    job_id = 'job_id_' + str(common_functions.get_unique_number_added_to_job_id(target_new_node))
                    JOB(task=target_new_node, job_id=job_id)
                    JOB.set_corresponding_task_form_initial_bpmn_by_job_id(job_id, target_node)

                    parent_job_id = JOB.get_job_id_by_task(target_node)
                    if JOB.get_choice_flag_by_id(parent_job_id):
                        JOB.set_choice_flag_by_id(job_id, True)

                for __excluded_input_node in __excluded_input_nodes:
                    ex_flow_tuple = (__excluded_input_node, target_new_node)
                    all_new_flows.add(ex_flow_tuple)
                    
                if target_node not in correspondings3:
                    correspondings3[target_node] = {target_new_node}
                else:
                    correspondings3[target_node].add(target_new_node)

                source_nodes.add(target_new_node)
                if target_node in _BPMN__node_annotations:
                    all_new_activities[target_new_node] = _BPMN__node_annotations[target_node]
                else:
                    all_new_activities[target_new_node] = ""

                affected_nodes_to_remove.add(target_node)
                for n_sources in new_activities:
                    new_tupplee = (n_sources, target_new_node)
                    main_source = find_key_by_value(correspondings3, n_sources)
                    main_target = find_key_by_value(correspondings3, target_new_node)
                    if check_if_there_is_flow_between(main_source, main_target, flows):
                        all_new_flows.add(new_tupplee)


                affected_flows_to_remove.add(flow_i)
            else:
                target_nodes = set()
                before_last_nodes.append(flow_i.source)
    
    if target_nodes:
        replicate_sub_nodes(bpmn_graph, start_of_loop, target_nodes, source_nodes, flows, end, new_end, all_new_activities, all_new_flows, affected_nodes_to_remove, affected_flows_to_remove, correspondings3, before_last_nodes, __connected_nodes)

def check_if_there_is_flow_between(source, target, flows):
    flag = False
    for flow in flows:
        if flow.source == source and flow.target == target:
            flag = True

    return flag

def return_input_nodes_in_BPMN(node, flows):
    input_nodes = set()
    for flow in flows:
        if flow.target == node:
            input_nodes.add(flow.source)

    return input_nodes

def return_output_nodes_in_BPMN(node, flows):
    output_nodes = set()
    for flow in flows:
        if flow.source == node:
            output_nodes.add(flow.target)

    return output_nodes

def find_key_by_value(my_dict, value):
    for key, val in my_dict.items():
        if value in val:
            return key
    return None

def find_SLURM_conditions(bpmn_info):
    condition_flows = {}
    for flow_id, flow_details in bpmn_info["_BPMN__flows_details"].items():
        if (flow_details["name"].startswith("SLURM:")) :
            condition_flows[flow_id] = {
                "SLURM_app": flow_details["name"],
                "source_node": flow_details["source_ref"],
                "target_node": flow_details["target_ref"]
            }

    return condition_flows

def process_conditions(bpmn_graph):
    bpmn_info = bpmn_graph.__dict__
    flows = bpmn_info['_BPMN__flows']
    condition_flows = find_SLURM_conditions(bpmn_info)
    affected_flows_to_remove = set()
    affected_flows = set()
    new_nodes = set()
    new_flows = set()

    for hidden_flow_id, hidden_flow_details in condition_flows.items():
        SLURM_app = hidden_flow_details['SLURM_app']
        SLURM_pure_app = SLURM_app.replace("SLURM:", "").strip()
        new_node = BPMN.Task(name=SLURM_pure_app)

        job_id = 'job_id_' + str(common_functions.get_unique_number_added_to_job_id(new_node))
        JOB(task=new_node, job_id=job_id)
        JOB.set_corresponding_task_form_initial_bpmn_by_job_id(job_id, new_node)

        parent_job_id = JOB.get_job_id_by_task(new_node)
        if JOB.get_choice_flag_by_id(parent_job_id):
            JOB.set_choice_flag_by_id(job_id, True)

        unique_number_added_to_job_id = job_id.split('job_id_')[1]

        command = SLURM_pure_app
        JOB.set_application_by_job_id(job_id, command)

        srun_file_name = unique_number_added_to_job_id + "_" + SLURM_pure_app.split('.')[0] + '.sh'
        JOB.set_srun_file_name_by_job_id(job_id, srun_file_name)
        JOB.set_choice_flag_by_id(job_id, True)

        new_nodes.add(new_node)

        source_node = hidden_flow_details['source_node']
        # for flow in flows:
            # if flow.target == source_node:
                # new_flow_tupple1 = (flow.source, new_node)
        new_flow_tupple1 = (source_node, new_node)
        new_flows.add(new_flow_tupple1)
                # affected_flows.add((flow.source, source_node))
                
        target_node = hidden_flow_details['target_node']
        new_flow_tupple2 = (new_node, target_node)
        new_flows.add(new_flow_tupple2)
        affected_flows.add((source_node, target_node))

    for a_flow in affected_flows:
        for flow_i in flows:
            if (flow_i.source == a_flow[0] 
                and flow_i.target == a_flow[1]):
                affected_flows_to_remove.add(flow_i)

    for n_node in new_nodes:
        bpmn_graph.add_node(n_node)

    for n_flow in new_flows:
        n_flow_obj = BPMN.SequenceFlow(n_flow[0], n_flow[1])
        bpmn_graph.add_flow(n_flow_obj)

    for a_flow in affected_flows_to_remove:
        bpmn_graph.remove_flow(a_flow)
    
    return bpmn_graph
