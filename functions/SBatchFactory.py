import sys, os
from os.path import dirname, abspath
filedir = dirname(abspath(__file__))
basedir = dirname(dirname(abspath(__file__)))
sys.path.insert(1, basedir)
from pm4py.objects.bpmn.obj import BPMN
import ast
from functions import BpmnUtils
from functions import ssh_connection
from functions.graph import Graph, Vertex
import random
import string

def is_folder(str_argu, HOST_SERVER, USERNAME_RWTH, PASSWORD_PATH):
    folder_content_list = list()
    try:
        ssh1 = ssh_connection.get_ssh_client(HOST_SERVER, USERNAME_RWTH, PASSWORD_PATH)
        # ssh_stdin, ssh_stdout, ssh_stderr = ssh1.exec_command("[ -d {0} ] && echo OK && ls {0}".format(str(str_argu)))
        # folder_content = ssh_stdout.read().decode('ascii')
        # folder_content_lines = folder_content.split("\n")

        ssh_stdin, ssh_stdout, ssh_stderr = ssh1.exec_command("[ -d {0} ] && echo OK && find {0} -type f".format(str(str_argu)))
        folder_content = ssh_stdout.read().decode('ascii')
        folder_content_lines = folder_content.split("\n")
        
        if len(folder_content_lines) > 1:
            is_folder = folder_content_lines[0]
            if is_folder.strip() == 'OK':
                for a_file in folder_content_lines[1:]:
                    if len(a_file) > 1:
                        folder_content_list.append(a_file)
                return True, folder_content_list
        else:
            folder_content_list.append(str_argu)
            return False, folder_content_list
    except Exception as e:
        folder_content_list.append(str_argu)
        return False, folder_content_list
    
def is_file(str_argu, HOST_SERVER, USERNAME_RWTH, PASSWORD_PATH):
    try:
        ssh1 = ssh_connection.get_ssh_client(HOST_SERVER, USERNAME_RWTH, PASSWORD_PATH)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh1.exec_command("[ -f '{0}' ] && echo 'OK' || echo 'Not a file'".format(str(str_argu)))
        return True
    except Exception as e:
        return False

def get_list(str_argu):
    return ast.literal_eval(str_argu)

def filter_flows(flows):
    filtered_flows = set()
    for flow in flows:
        if isinstance(flow.source, BPMN.Task) and isinstance(flow.target, BPMN.Task):
            filtered_flows.add(flow)
    return filtered_flows

# here is an example how this code works
# arguments=[['1', '2'], ['c']]
# output = ['1 c', '2 c']
def generate_combs(arguments, combos, index):
    if index == len(arguments):
        return combos
    
    c = get_list(arguments[index])
    new_combos = []
    if len(combos) == 0:
        for item in c:
            new_combos.append(item)
    else:
        for item in c:            
            for x in combos:
                new_combos.append(x + " " + item)
    
    return generate_combs(arguments, new_combos, index + 1)
def extract_values(command, data_dict):
    parts = command.split()
    extracted_values = []
    for part in parts:
        if part.startswith("$") and part[1:] in data_dict:
            extracted_values.append(data_dict[part[1:]])
    return extracted_values

def create(processed_bpmn, should_be_uploaded_list, bpmn_info, local_exe_filename, remoteserver_info):

    # we need these credentials to check if an arguments in a folder of not (for that we have to contact)
    # to the cluster simply check if it is a folder or not
    HOST_SERVER = remoteserver_info['serverhost']
    USERNAME_RWTH = remoteserver_info['username']
    PASSWORD_PATH = remoteserver_info['password']

    nodes = processed_bpmn['_BPMN__nodes']
    flows = processed_bpmn['_BPMN__flows']
    node_flow_groups = processed_bpmn['node_flow_groups']
    node_info = BpmnUtils.convert_input_to_dict_output(processed_bpmn['_BPMN__node_annotations'])
    args_dict = {}
    for key, value in node_info.items():
        sbatch_command = f"{key.replace(' ', '_')}.sh"
        value['sbatch_command'] = sbatch_command

        if 'srun_command' in value:
            command = value['srun_command']
            values = extract_values(command, value)
            args_dict[key] = values
    # we have Vertex class, that for each node we create a Vertex that has
    # one id, name, and a command
    # here we want to create a vertex for each node
    # nodes_vertex assign 'pm4py.objects.bpmn.obj.BPMN.NormalEndEvent' and 'pm4py.objects.bpmn.obj.BPMN.Task' types to 'general.SBatchFactory.Vertex'
    vertices = list()
    nodes_vertex = dict()
    for node in nodes:
        if str(node) in node_info:
            command = node_info[str(node)]['sbatch_command']
            srun_command_parts = str(node_info[str(node)]['srun_command']).strip().split(' ')
            srun_command = srun_command_parts[0] if srun_command_parts else ''
        else:
            command = ''
            srun_command = ''
        
        print("step 1")
        print("str(node): ", str(node))
        print("command: ", command)
        print("srun_command: ", srun_command)
        print("step 3")
        v = Vertex(str(node), command, srun_command)
        nodes_vertex[node] = v
        vertices.append(v)

    
    # we need to have flows in vertex type, which vertex goes to which one?
    # here type(flow) is 'pm4py.objects.bpmn.obj.BPMN.SequenceFlow'
    # and type(flow.source) is 'pm4py.objects.bpmn.obj.BPMN.Task'
    filtered_flows = filter_flows(flows)
    edges = list()
    for flow in filtered_flows:
        edge = (nodes_vertex[flow.source], nodes_vertex[flow.target])
        if edge not in edges:
            edges.append(edge)

    # now that we have vertices and edges lets create the Graph
    g = Graph()
    for vertex in vertices:
        g.add_vertex(vertex)
    for edge in edges:
        g.add_edge(edge)

    for element in args_dict:
        x = generate_combs(args_dict[element], [], 0)
        args_dict[element] = [str(x)]

    # why?
    reverse_order_vertices = g.topological_sort()
    reverse_order_vertices.reverse()


    labels = {}
    CI = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    for vtx in reverse_order_vertices:
        # get corresponding vertex
        verttex = g.lookup(vtx.name)

        labels[str(verttex)] = CI

        if str(verttex) in args_dict:
            argus = args_dict[str(verttex)]
            for argument in argus:               
                convert_to_list = get_list(argument)
                if len(convert_to_list) > 1:
                    g.replicate_subgraph(verttex, convert_to_list, args_dict, filtered_flows, nodes_vertex, node_flow_groups, labels)
                elif len(convert_to_list) == 1:
                    print("we want to check if {} is a folder.".format(convert_to_list[0]))
                    # TODO: how to create richtig input values
                    folder_state, folder_content = is_folder(convert_to_list[0], HOST_SERVER, USERNAME_RWTH, PASSWORD_PATH)
                    if folder_state:
                        if len(folder_content) > 1:
                            contents_path = [os.path.join(convert_to_list[0], item) for item in folder_content]
                            # is_file(contents_path[0], HOST_SERVER, USERNAME_RWTH, PASSWORD_PATH)
                            args_dict[str(verttex)] = "[\"" + str(contents_path) + "\"]"
                            g.replicate_subgraph(verttex, folder_content, args_dict, filtered_flows, nodes_vertex, node_flow_groups, labels)
                    else:
                        args_dict[str(verttex)] = str(folder_content[0])
                else:
                    args_dict[str(verttex)] = ""

    script = g.generate_script(args_dict, node_flow_groups, labels, CI)
    local_exe_path = os.path.join(bpmn_info['directorypath'], local_exe_filename)
    F = open(local_exe_path, "w")
    should_be_uploaded_list.append(str(local_exe_path))
    F.write(script)
    F.close()