import random
import copy
import string

class Vertex(object):
    next_id = 0
    def __init__(self, name, sbatch_command, srun_command):
        self.id = Vertex.next_id
        self.name = name
        self.sbatch_command = sbatch_command
        self.srun_command = srun_command
        self.vertex_input_files = {}
        Vertex.next_id += 1

    def add_parameter(self, key, value):
        self.vertex_input_files[key] = value

    def get_parameter(self, key):
        return self.vertex_input_files.get(key)
    
    def __repr__(self):
        return self.name

class Graph(object):
    def __init__(self):
        self._graph_dict = {}
        self._graph_dict_rev = {}
        self.caseids = {}

    def edges(self, vertice):
        return self._graph_dict[vertice]

    def all_vertices(self):
        return set(self._graph_dict.keys())

    def all_edges(self):
        return self.__generate_edges()

    def add_vertex(self, vertex):
        if vertex not in self._graph_dict:
            self._graph_dict[vertex] = []
            self._graph_dict_rev[vertex] = []

    def add_edge(self, edge):
        vertex1, vertex2 = edge
        if vertex2 not in self._graph_dict[vertex1]:
            self._graph_dict[vertex1].append(vertex2)
        if vertex1 not in self._graph_dict_rev[vertex2]:
            self._graph_dict_rev[vertex2].append(vertex1)

    def topological_sort(self):
        graph_dict_rev = copy.deepcopy(self._graph_dict_rev)
        vertices_sorted = []
        while len(graph_dict_rev.keys()) > 0:
            for vertex in graph_dict_rev.keys():
                if len(graph_dict_rev[vertex]) == 0:
                    vertices_sorted.append(vertex)
                    for v in graph_dict_rev.keys():
                        if vertex in graph_dict_rev[v]:
                            graph_dict_rev[v].remove(vertex)
                    graph_dict_rev.pop(vertex)
                    break
        
        return vertices_sorted

    def reachable_subgraph(self, vertex):
        reachable = set()
        processing = [vertex]

        while len(processing) > 0:
            next_vertex = processing[0]
            reachable.add(next_vertex)
            children = self._graph_dict[next_vertex]
            processing += children
            processing.remove(next_vertex)

        return reachable

    # for each subvertex in subgraph 
    # create a new vertex with 
    # different name that is based on the i and a random value
    # with the same command
    def corresponding_vertices(self, subgraph, i, node_flow_groups, labels, prefix):
        # prefix is the str format of i that is used for CI
        # and after updating the prefix the labels will be updated
        corresponding_vertices_dict = dict()
        for sub_vertex in subgraph:
            new_vertex_name = sub_vertex.name + "__" + str(i) + "_" + str(random.randint(0, 100000000))
            if str(sub_vertex) in node_flow_groups:
                node_flow_groups[str(new_vertex_name)] = node_flow_groups[str(sub_vertex)]
            
            print("sub_vertex: ", sub_vertex)
            new_vertex = Vertex(new_vertex_name, sub_vertex.sbatch_command, '')
            self.add_vertex(new_vertex)
            corresponding_vertices_dict[sub_vertex] = new_vertex
            if str(sub_vertex) in labels:
                labels[str(new_vertex)] = prefix + "-" + labels[str(sub_vertex)]
            else:
                labels[str(new_vertex)] = prefix

        return corresponding_vertices_dict

    def replicate_subgraph(self, vertex, arguments_list, args_dict, flows, nodes_vertex, node_flow_groups, labels):
        # we see all the nodes that are reachable form the current vertex + itself
        subgraph = self.reachable_subgraph(vertex)

        # here we get the first element of the arguments list
        args_dict[str(vertex)] = str(arguments_list[0])

        # For arguments_list = [a, b], the loop is on range(1,2), which mean starts from 1 to 1
        # since we already have the first argument in args_dict[str(vertex)] we start the loop from second element
        # which is in the index 1
        for i in range(1, len(arguments_list)):
            item = arguments_list[i]
            # so we create the corresponding index here and assign an CI to it and with the two next lines we also assign the argument to it
            corresponding_vertices_dict = self.corresponding_vertices(subgraph, i, node_flow_groups, labels, str(i))
            vertex_prim = corresponding_vertices_dict[vertex]
            args_dict[str(vertex_prim)] = str(item)

            for v in subgraph:
                v_prim = corresponding_vertices_dict[v]
                # now that we have the v_prime we want to add the edges
                children = self._graph_dict[v]
                for child in children:
                    if child in corresponding_vertices_dict:
                        child_prim = corresponding_vertices_dict[child]
                        # give the child prime the same arguments
                        args_dict[str(child_prim)] = args_dict[str(child)]
                        self.add_edge((v_prim, child_prim))
                
                parent = self._graph_dict_rev[v]
                for p in parent:
                    if p in subgraph:
                        p_prim = corresponding_vertices_dict[p]
                        self.add_edge((p_prim, v_prim))
                    else:
                        self.add_edge((p, v_prim))

        for v in subgraph:
            labels[str(v)] = "0-" + labels[str(v)]

    def assign_case_ids(self):
        self.caseids = {}
        # ...
    
    def lookup(self, name):
        for v in self._graph_dict:
            if v.name == name:
                return v

    def generate_script(self, order):
        print()
        print(order)
        script = "#!/usr/local_rwth/bin/bash\n\n"
        script += 'FILES_DIR=$(echo $RANDOM | md5sum | head -c 8)\n'
        script += 'FILES_DIR="{}_$FILES_DIR"\n'.format("__TODO__")
        script += 'mkdir $FILES_DIR\n'
        
        # order = self.topological_sort()

        # for vertex in order:
        #     v = self.lookup(vertex.name)
        #     v.output_file = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

        for vertex in order:
        #     vertex_case_id = labels[vertex.name]
            # if vertex.sbatch_command == "":
            #     continue
        #     deps = []
            v = self.lookup(vertex.name)
            deps = self._graph_dict_rev[v]

            # input_file_list = list()
            # for o_dep in deps:
            #     input_file_list.append(o_dep.output_file)

            # v.input_file = " ".join(input_file_list)

            deps_str = ""
            for dep in deps:
        #     #     if dep.sbatch_command == "":
        #     #         continue
                deps_str += ("--dependency=afterfork:$JOB_ID_" + str(dep.id)) + " "

            script += "JOB_ID_" + str(v.id) + "=$(sbatch --parsable " + deps_str + "$FILES_DIR " + v.srun_command + ")\n"
        #     has_deps = False
        #     if len(deps) > 0:
        #         for dep in deps:
        #             if dep.sbatch_command != "":
        #                 has_deps = True

        #     if has_deps:
        #         #TODO: add afterany
        #         deps_str = "--dependency=afterok:"
        #     else:
        #         deps_str = ""

        #     for i, dep in enumerate(deps):
        #         dep_str = ""
        #         if dep.sbatch_command == "":
        #             dep_str = ""
        #             continue
                
        #         dep_str = "$JOB_ID_" + str(dep.id)
        #         if i + 1 == len(deps):
        #             deps_str += dep_str + " "
        #         else:
        #             if str(vertex) in node_flow_groups:
        #                 if node_flow_groups[str(vertex)] == 'or':
        #                     deps_str += dep_str + "?"
        #                 else:
        #                     deps_str += dep_str + ","
            

        #     vcommand_str = ""
        #     if len(v.sbatch_command) > 0:
        #         vcommand_str = v.sbatch_command + " "

        #     arguments_value__str = ""
        #     if len(args_dict[v.name]) > 0:
        #         arguments_value__str = args_dict[v.name] + " "

        #     vinput_file__str = str(len(input_file_list)) + " "
        #     if len(v.input_file) > 0:
        #         vinput_file__str +=  v.input_file + " "

        #     voutput_file__str = ""
        #     if len(v.output_file) > 0:
        #         voutput_file__str = v.output_file + " "

        #     vertex_input_files = ""
            
        #     #TODO: needs to be fixed in case of the choice
        #     ghost_flag = True
        #     for parent_v in self._graph_dict_rev[v]:
        #         if '___ghost___' in parent_v.name or '___fake___' in parent_v.name:
        #             vertex_input_files = parent_v.get_parameter("ghost_param")
        #             v.input_file = parent_v.input_file
        #             ghost_flag = False

        #     if ghost_flag:
        #         vertex_input_files = vinput_file__str
            
        #     #TODO: test many times
        #     v.add_parameter("ghost_param", vertex_input_files)
        #     script += "JOB_ID_" + str(v.id) + "=$(sbatch --parsable " + deps_str + vcommand_str + "$FILES_DIR " + vertex_input_files + voutput_file__str + arguments_value__str + vertex_case_id + " " + v.srun_command + ")\n"
        
        print("---"*20)
        print(script)
        print("---"*20)
        return script