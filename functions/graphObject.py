import hashlib
from pm4py.algo.simulation.playout.petri_net.variants import basic_playout
from pm4py.objects.petri_net.obj import PetriNet
from pm4py.objects.bpmn.obj import BPMN

class JOB:
    _instances = []
    def __init__(self, task, job_id, application=None, dependency_script=None, 
                 input_files=set(), output_file=set(), srun_file_name=None, 
                 corresponding_task_from_initial_bpmn="", choice_flag=False):
        self.task = task
        self.job_id = job_id
        self.application = application
        self.dependency_script = dependency_script
        self.input_files = set()
        self.output_file = set()
        self.srun_file_name = srun_file_name
        self.corresponding_task_from_initial_bpmn = ""
        self.choice_flag = False

        # Add the new instance to the class variable list
        JOB._instances.append(self)

    def set_task(self, task):
        self.job_id = task

    def get_task(self):
        return self.task

    def get_job_id(self):
        return self.job_id
    
    def set_application(self, application):
        self.application = application

    def get_application(self):
        return self.application
    
    def set_dependency_script(self, dependency_script):
        self.dependency_script = dependency_script

    def get_dependency_script(self):
        return self.dependency_script
    
    def add_input_file(self, input_file):
        self.input_files.add(input_file)

    def get_input_files(self):
        return list(self.input_files)
    
    def add_output_file(self, output_file):
        self.output_file.add(output_file)

    def get_output_file(self):
        return list(self.output_file)
    
    @classmethod
    def get_output_file_by_job_id(cls, job_id):
        for job in cls._instances:
            if job.get_job_id() == job_id:
                return job.get_output_file()
        return False
    
    def set_srun_file_name(self, srun_file_name):
        self.srun_file_name = srun_file_name

    def get_srun_file_name(self):
        return self.srun_file_name
    
    def set_choice_flag(self, flag):
        self.choice_flag = flag

    def get_choice_flag(self):
        return self.choice_flag
    
    def get_corresponding_task_from_initial_bpmn(self):
        return self.corresponding_task_from_initial_bpmn
    
    def set_corresponding_task_from_initial_bpmn(self, old_task):
        self.corresponding_task_from_initial_bpmn = old_task

    @classmethod
    def set_corresponding_task_form_initial_bpmn_by_job_id(cls, job_id, old_task):
        """Set the dependency_script value for the job with the given job_id."""
        for job in cls._instances:
            if job.get_job_id() == job_id:
                job.set_corresponding_task_from_initial_bpmn(old_task)
                return True
        return False

    @classmethod
    def get_all_jobs(cls):
        return cls._instances
    
    @classmethod
    def set_srun_file_name_by_job_id(cls, job_id, new_srun_file_name):
        for job in cls._instances:
            if job.get_job_id() == job_id:
                job.set_srun_file_name(new_srun_file_name)
                return True
        return False
    
    @classmethod
    def set_dependency_script_by_job_id(cls, job_id, new_dependency_script):
        for job in cls._instances:
            if job.get_job_id() == job_id:
                job.set_dependency_script(new_dependency_script)
                return True
        return False
    
    @classmethod
    def set_application_by_job_id(cls, job_id, new_application):
        for job in cls._instances:
            if job.get_job_id() == job_id:
                job.set_application(new_application)
                return True
        return False
    
    @classmethod
    def set_choice_flag_by_id(cls, job_id, flag):
        for job in cls._instances:
            if job.get_job_id() == job_id:
                job.set_choice_flag(flag)
                return True
        return False
    
    @classmethod
    def get_choice_flag_by_id(cls, job_id):
        for job in cls._instances:
            if job.get_job_id() == job_id:
                return job.get_choice_flag()
        return False
    
    @classmethod
    def get_job_id_by_task(cls, task):
        for job in cls._instances:
            if job.get_task() == task:
                return job.get_job_id()
        return False

    @classmethod
    def add_input_file_by_job_id(cls, job_id, new_input_file):
        for job in cls._instances:
            if job.get_job_id() == job_id:
                job.add_input_file(new_input_file)
                return True
        return False

    @classmethod
    def add_output_file_by_job_id(cls, job_id, new_output_file):
        for job in cls._instances:
            if job.get_job_id() == job_id:
                job.add_output_file(new_output_file)
                return True
        return False
    
    @classmethod
    def get_task_by_job_id(cls, job_id):
        for job in cls._instances:
            if job.get_job_id() == job_id:
                return job.task
        return None

    @classmethod
    def get_job_id_by_task(cls, task):
        for job in cls._instances:
            if job.task == task:
                return job.get_job_id()
        return None
    
    @classmethod
    def remove_all_jobs(cls):
        """Remove all job instances."""
        cls._instances.clear()

    @classmethod
    def remove_job_by_id(cls, job_id):
        """Remove the job instance with the specified job_id."""
        cls._instances = [job for job in cls._instances if job.get_job_id() != job_id]
        return True

def get_transition(net, node):
    for tran in net.transitions:
        if tran.label == node:
            return tran
        else:
            continue

def find_runs(net, im, fm):
    sequences = basic_playout.apply(net, im, fm)
    runs = []
    for trace in sequences:
        trace_set = {event['concept:name'] for event in trace}
        if trace_set not in runs:
            runs.append(trace_set)

    new_runs = {}
    for idx, run in enumerate(runs):
        new_run = set()
        for node in run:
            new_run.add(get_transition(net, node))
        
        new_runs[f"run_{idx}"] = new_run

    return new_runs

def find_choice_part_in_petrinet(places, source_trans, first_source_trans, unique_trans):
    for source_tran in list(source_trans):
        for f_source_tran in first_source_trans:
            if f_source_tran not in unique_trans:
                unique_trans[f_source_tran] = set()

        for place in places:
            out_arcs = place.out_arcs
            for arc in out_arcs:
                if arc.target == source_tran:
                    source_place = arc.source
                    in_arcs = source_place.in_arcs
                    if len(in_arcs) > 0:
                        new_source_trans = set()
                        for in_arc in in_arcs:
                            new_source_tran = in_arc.source
                            if new_source_tran.label:
                                if source_tran in unique_trans:
                                    unique_trans[source_tran].add(new_source_tran)
                                else:
                                    for unique_tran in unique_trans:
                                        if source_tran in unique_trans[unique_tran]:
                                            unique_trans[unique_tran].add(new_source_tran)
                                    

                                new_source_trans.add(new_source_tran)
                                find_choice_part_in_petrinet(places, new_source_trans, first_source_trans,  unique_trans)


def go_foward_until_end_of_choice(net, first_tran, tran, choice_options):
    places =  net.places
    for place in places:
        in_arcs = place.in_arcs
        for in_arc in in_arcs:
            if in_arc.source == tran:
                out_arcs = place.out_arcs
                for out_arc in out_arcs:
                    if out_arc.target.label:
                        choice_options[first_tran].add(out_arc.target)
                        go_foward_until_end_of_choice(net, first_tran, out_arc.target, choice_options)
                    else:
                        go_foward_until_end_of_choice(net, first_tran, out_arc.target, choice_options)

    
                    
def remove_common_elements(choice_options):
    common_elements = set.intersection(*choice_options.values())
    for key, value in choice_options.items():
        choice_options[key] = value - common_elements
    return choice_options

def discard_alternatives(value, alternetives):
    value_copy = value.copy()
    for alternative_ in alternetives:
        for alter_element in alternative_:
            if alter_element in value_copy:
                value_copy.discard(alter_element)

    return value_copy

def find_combination_of_choice_parts(all_unique_parts):
    print("-----"*20)
    combined_unique_parts = dict()
    for unique_part_collection in all_unique_parts:
        for key1, value1 in unique_part_collection.items():
            combined_unique_parts[key1] = value1
    
    sorted_unique_parts = dict(sorted(combined_unique_parts.items(), key=lambda item: len(item[1]), reverse=True))
    
    final_runs_unique_parts = list()
    for key, value in sorted_unique_parts.items():
        nested_run = False
        for val in value:
            if val != key:
                if val in sorted_unique_parts:
                    nested_run = True
        
        if nested_run:
            print()
            print("++++"*20)
            probably_cannot_be_run_together = list()
            for unique_part_collection2 in all_unique_parts:
                choices = list()
                for key2, val2 in unique_part_collection2.items():
                    choices.append(val2)

                if len(choices)>0:
                    probably_cannot_be_run_together.append(choices)

            unique_set_of_elements = list()
            for val in list(value):
                if val != key:
                    if val in sorted_unique_parts:
                        the_choice, alternetives = find_alternetives(val, probably_cannot_be_run_together, combined_unique_parts)
                        value_copy = discard_alternatives(value, alternetives)                        

                        print()
                        the_choice_task = list(the_choice)[0]
                        print("the_choice_task: ", the_choice_task)
                        for job in JOB.get_all_jobs():
                            job_task = job.get_task()
                            if the_choice_task.name == job_task.id:
                                the_choice_corersponding_task = job.get_corresponding_task_from_initial_bpmn()
                                for val_copy in value_copy:
                                    if val_copy != the_choice_task:
                                        for job2 in JOB.get_all_jobs():
                                            job2_task = job2.get_task()
                                            if val_copy.name == job2_task.id:
                                                val_copy_corersponding_task = job2.get_corresponding_task_from_initial_bpmn()
                                                if the_choice_corersponding_task == val_copy_corersponding_task:
                                                    print("val_copy", val_copy)
                                                    the_choice_val_copy, alternetives_val_copy = find_alternetives(val_copy, probably_cannot_be_run_together, combined_unique_parts)
                                                    value_copy2 = discard_alternatives(value_copy, alternetives_val_copy)

                        if value_copy2 not in unique_set_of_elements:
                            unique_set_of_elements.append(value_copy2)


            
            for itemmmm in unique_set_of_elements:
                print()
                print()
                print()
                for nnnn in itemmmm:
                    print("____: ", nnnn.label)


    #         nested_parts = list()
    #         for val in list(value):
    #             if val != key:
    #                 if val in sorted_unique_parts:
    #                     val_value = sorted_unique_parts[val]
    #                     nested_parts.append(val_value)
    #                     for item in val_value:
    #                         value.discard(item)
            
    #         for nested_part in nested_parts:
    #             combined_set = value.union(nested_part)
    #             final_runs_unique_parts.append(combined_set)
            print("++++"*20)
            print()
        else:
            print("there is no nested node")
            final_runs_unique_parts.append(value)

    return final_runs_unique_parts

def find_alternetives(node, probably_cannot_be_run_together, combined_unique_parts):
    the_choice = list()
    alternetives = list()
    for item in probably_cannot_be_run_together:
        for choice in item:
            for element in choice:
                if element == node:
                    the_choice = combined_unique_parts[element]

        if the_choice in item:
            alternetives = [element for element in item if element != the_choice]

    return the_choice, alternetives

def find_runs2(net, im, fm):
    places = net.places
    all_unique_parts = list()
    for place in places:
        if len(place.out_arcs) > 1:
            output_trans_labels = list()
            for out_arc in place.out_arcs:
                if out_arc.target.label:
                    output_trans_labels.append(out_arc.target)

            if len(output_trans_labels) > 1:
                choice_options = {}
                for output_tran in output_trans_labels:
                    choice_options[output_tran]=set()
                    choice_options[output_tran].add(output_tran)
                    go_foward_until_end_of_choice(net, output_tran, output_tran, choice_options)
                
                unique_parts = remove_common_elements(choice_options)
                
                all_unique_parts.append(unique_parts)  
    
    final_runs_unique_parts = find_combination_of_choice_parts(all_unique_parts) 

    #     in_arcs = place.in_arcs
    #     if len(in_arcs) > 0:
    #         if len(in_arcs) > 1:
    #             source_trans = set()
    #             for in_arc in in_arcs:
    #                 source_tran = in_arc.source
    #                 if source_tran.label:
    #                     source_trans.add(source_tran)

    #             if len(source_trans) > 1:
    #                 find_choice_part_in_petrinet(places, source_trans, source_trans, unique_trans)
    #             else:
    #                 continue

    # transitions = net.transitions
    # visible_transitions = set()
    # for transition in transitions:
    #     if transition.label:
    #         visible_transitions.add(transition)

    # unique_trans_tuples = {tuple([key] + list(values)) for key, values in unique_trans.items()}
    # flat_set = {element for subset in unique_trans_tuples for element in subset}
    # difference_transitions_to_flat = visible_transitions - flat_set
    # updated_unique_trans_list = list()
    # if len(unique_trans_tuples) > 0:
    #     for unique_trans_tupe in unique_trans_tuples:
    #         unique_trans_set = set(unique_trans_tupe)
    #         merged_set = unique_trans_set | difference_transitions_to_flat
    #         updated_unique_trans_list.append(merged_set)
    # else:
        # updated_unique_trans_list.append(difference_transitions_to_flat)

    new_runs = {}
    # for idx, run in enumerate(updated_unique_trans_list):
    #     new_run = set()
    #     for node in run:
    #         new_run.add(node)
        
    #     new_runs[f"run_{idx}"] = new_run

    return new_runs

def runs_and_inputs_factory(net, im, fm):
    runs = find_runs2(net, im, fm)
    all_inputs_dict = {}
    for index, run in runs.items():
        inputs_dict = inputs(net, run)
        all_inputs_dict[index] = inputs_dict

    return runs, all_inputs_dict

def inputs(net, run):
    inputs_dict = {}
    arcs =  net.arcs
    for arc in arcs:
        if isinstance(arc.target, PetriNet.Transition) and arc.target in run:
            source_place = arc.source    
            in_arcs = source_place.in_arcs
            if len(in_arcs) > 0:
                return_inputs(run, arc, in_arcs, inputs_dict, net)

    for task in run:
        if task not in inputs_dict:
            inputs_dict[task] = []

    return inputs_dict

def return_inputs(run, arc, in_arcs, inputs_dict ,net):
    for arc2 in in_arcs:
        source_tran = arc2.source
        if source_tran.label == None:
            for place in net.places:
                for out_arc in place.out_arcs:
                    if out_arc.target == source_tran:
                        for in_arc in place.in_arcs:
                            return_inputs(run, arc, place.in_arcs, inputs_dict, net)
        else:
            if source_tran in run:
                if arc.target in inputs_dict:
                    if source_tran not in inputs_dict[arc.target]:
                        inputs_dict[arc.target].append(arc2.source)
                    else:
                        continue
                else:
                    inputs_dict[arc.target] = [source_tran]

def dependency_script_factory(runs, inputs_dict):
    processed_tasks = {}
    depend_script = {}
    job_ids = {}
    should_be_uploaded_list = set()
    for index, run in runs.items():
        run_inputs = inputs_dict[index]
        for task in run:
            if task in processed_tasks:
                the_job_id = job_ids[task]
                old_inputs = processed_tasks[task]
                new_inputs = run_inputs[task]
                if set(old_inputs) != set(new_inputs):
                    old_dep_str = depend_script[the_job_id]
                    old_job_ids, old_job_deps_str =  extract_dependencies(old_dep_str)
                    for n_input in new_inputs:
                        if n_input not in processed_tasks:
                            add_dependency(n_input, run_inputs, depend_script, job_ids, processed_tasks, [], should_be_uploaded_list)

                    new_input_job_ids = [job_ids[e_in] for e_in in new_inputs]
                    updated_job_ids = update_job_ids(old_job_ids, new_input_job_ids)
                    new_job_ids_str = construct_dependencies_str(updated_job_ids)
                    new_dep_str = old_dep_str.replace(old_job_deps_str, new_job_ids_str)
                    new_dep_str = new_dep_str.replace('afterok','afterany')
                    depend_script[the_job_id] = new_dep_str     
            else:
                add_dependency(task, run_inputs, depend_script, job_ids, processed_tasks, [], should_be_uploaded_list)

    return depend_script, should_be_uploaded_list

def extract_dependencies(input_str):
    start = input_str.index(":") + 1
    end = input_str[start:].index(" ") + start
    sub_text_of_dependecies = input_str[start:end]
    dependencies = sub_text_of_dependecies.split(',')

    

    striped_dependencies = []
    for dependency in dependencies:
        striped_dependency = dependency.replace('$', '').replace('afterany:', '').replace('afterok:', '')
        striped_dependencies.append(striped_dependency)

    
    split_dependency_list = [item.split(":") for item in striped_dependencies]
    striped_split_dependency_list = [[sub_item.strip() for sub_item in sublist] for sublist in split_dependency_list]
    
    return striped_split_dependency_list, sub_text_of_dependecies


def get_job_application_from_label(task):
    task_label = task.label
    command = task_label.split('.')[0] if '.' in task_label else task_label
    return command.strip()


def get_command_from_label(task):
    label = task.label
    command =  label
    if '__aff_iloop__' in label:
        parts = label.split('__aff_iloop__')
        if len(parts) > 1:
            command = parts[1]
    elif '__aff_eloop__' in label:
        parts = label.split('__aff_eloop__')
        if len(parts) > 1:
            command = parts[1]
    
    command_parts = command.split('=')
    if len(command_parts)>1:
        command = command_parts[1].strip()
        output = command_parts[0].strip()
    else:
        command = command_parts[0].strip()
        output = None

    return command

def add_dependency(task, run_inputs, depend_script, job_ids, processed_tasks, j_dep_list, should_be_uploaded_list):
    # based on the name of the application needs to be run on SLURM and the task id we generate a unique a name for our bash file
    # that contains srun and parameter settings

    task_name = task.name

    for job in JOB.get_all_jobs():
        job_task = job.get_task()
        if job_task.id == task_name:
            job_id = job.get_job_id_by_task(job_task)

    unique_number_added_to_job_id = job_id.split('job_id_')[1]
    srun_file_name = unique_number_added_to_job_id + "_" + get_job_application_from_label(task) + '.sh'
        
    JOB.set_srun_file_name_by_job_id(job_id, srun_file_name)
    command = get_command_from_label(task)
    JOB.set_application_by_job_id(job_id, command)
    # we also need a job id that refers to srun file in our sbatch file
    
    if job_id not in job_ids:
        job_ids[task] = job_id

    if not run_inputs[task]: # no dependency
        depend_script[job_id] = str(srun_file_name)
        processed_tasks[task] = run_inputs[task]
        j_dep_list = []
    elif len(run_inputs[task]) == 1:  # single dependency
        y = run_inputs[task][0]
        if y not in job_ids:
            j_dep_list = []
            add_dependency(y, run_inputs, depend_script, job_ids, processed_tasks, j_dep_list, should_be_uploaded_list)

        j_y = job_ids[y]
        depend_script[job_id] = f"--dependency=afterok:${j_y} {srun_file_name}"
        processed_tasks[task] = run_inputs[task]
    else:  # multiple dependencies
        for input in run_inputs[task]:
            if input not in job_ids:
                add_dependency(input, run_inputs, depend_script, job_ids, processed_tasks, j_dep_list, should_be_uploaded_list)

            processed_tasks[task] = run_inputs[task]
            j_dep_list.append(job_ids[input])

        depend_script[job_id] = f"--dependency=afterok:{','.join(['$' + j_dep for j_dep in j_dep_list])} {srun_file_name}"

def update_job_ids(old_job_ids, new_input_job_ids):
    for new_job_id in new_input_job_ids:
        found = False
        for sublist in old_job_ids:
            if new_job_id in sublist:
                found = True
                break
        if not found:
            for sublist in old_job_ids:
                if not any(job_id in sublist for job_id in new_input_job_ids if job_id != new_job_id):
                    sublist.append(new_job_id)
                    break
    old_job_ids.sort(key=len,reverse=True)          
    return old_job_ids

def construct_dependencies_str(updated_job_ids):
    dependencies = []
    first_list = updated_job_ids[0]
    
    first_dependencies = ":".join(["$" + job_id for job_id in first_list])
    dependencies.append(first_dependencies)
    
    for job_ids in updated_job_ids[1:]:
        if len(job_ids) > 1:
            dependency = ":".join(["$" + job_id for job_id in job_ids])
            dependency = f"afterany:{dependency}"
        else:
            dependency = f"${job_ids[0]}"
        dependencies.append(dependency)
    
    return ",".join(dependencies)

def output_and_input_files_factory(bpmn):
    _BPMN__data_objects = bpmn.__dict__['_BPMN__data_objects']
    _nodes = bpmn.__dict__['_BPMN__nodes']
    node_ids = [node.id for node in _nodes]

    for data_object in _BPMN__data_objects:
        data_object_details = _BPMN__data_objects[data_object]
        data_obj_name = data_object_details['name']
        source_ref_id = data_object_details['source_ref']
        target_ref_ids = data_object_details['target_ref']
        if source_ref_id in node_ids:
            if len(target_ref_ids) == 0:
                for job in JOB.get_all_jobs():
                    job_task = job.get_task()
                    job_task_id = job_task.id
                    job_id = job.get_job_id()
                    if job_task_id == source_ref_id:
                        job.add_output_file_by_job_id(job_id, data_obj_name)
            else:
                for target_ref_id in target_ref_ids:
                    if target_ref_id in node_ids:
                        for job in JOB.get_all_jobs():
                            job_task = job.get_task()
                            job_task_id = job_task.id
                            job_id = job.get_job_id()
                            if job_task_id == source_ref_id:
                                job.add_output_file_by_job_id(job_id, data_obj_name)

                            if job_task_id == target_ref_id:
                                job.add_input_file_by_job_id(job_id, data_obj_name)
        elif len(source_ref_id)==0:
            for target_ref_id in target_ref_ids:
                if target_ref_id in node_ids:
                    for job in JOB.get_all_jobs():
                        job_task = job.get_task()
                        job_task_id = job_task.id
                        job_id = job.get_job_id()
                        if job_task_id == target_ref_id:
                            job.add_input_file_by_job_id(job_id, data_obj_name)



def first_polishing(bpmn):
    _nodes = bpmn.__dict__['_BPMN__nodes']
    _tasks = set()
    for _node in _nodes:
        if isinstance(_node, BPMN.Task):
            _tasks.add(_node)

    for job in JOB.get_all_jobs():
        job_task = job.get_task()
        if job_task in _tasks:
            pass
        else:
            JOB.remove_job_by_id(job.get_job_id())
            
def find_previous_nodes(node, bpmn, previous_nodes):
    _flows = bpmn.__dict__['_BPMN__flows']

    for _flow in _flows:
        if _flow.target == node:
            if isinstance(_flow.source, BPMN.Task):
                previous_nodes.add(_flow.source)
                find_previous_nodes(_flow.source, bpmn, previous_nodes)
            else:
                if isinstance(_flow.source, BPMN.ParallelGateway):
                    find_previous_nodes(_flow.source, bpmn, previous_nodes)
                else:
                    if isinstance(_flow.source, BPMN.ExclusiveGateway):
                        print("_flow.source: ", _flow.source, type(_flow.source))
                    else:
                        pass
                    

    return previous_nodes

def update_inputs_for_choice_tasks(connected_jobs, bpmn):
    
    for job in JOB.get_all_jobs():
        if job.get_choice_flag():
            choice_node_id = job.get_job_id()
            choice_node = job.get_task()
            previous_nodes = set()
            find_previous_nodes(choice_node, bpmn, previous_nodes)
            for sublist in connected_jobs:
                if choice_node_id in sublist:
                    connected_job_ids = sublist
            
            for connected_job in connected_job_ids:
                connected_job_output_file = JOB.get_output_file_by_job_id(connected_job)
                if len(connected_job_output_file) > 0:
                    if connected_job_output_file[0]:
                        JOB.add_input_file_by_job_id(choice_node_id, connected_job_output_file[0])

def create(petri_net, im, fm, bpmn):
    runs, all_inputs_dict = runs_and_inputs_factory(petri_net, im, fm)
    depend_script, should_be_uploaded_list = dependency_script_factory(runs, all_inputs_dict)
    
    for job_id_dep in depend_script:
        JOB.set_dependency_script_by_job_id(job_id_dep, depend_script[job_id_dep])

    output_and_input_files_factory(bpmn)
    first_polishing(bpmn)
    connected_jobs = find_connected_jobs(runs , bpmn)
    update_inputs_for_choice_tasks(connected_jobs, bpmn)

    return depend_script, should_be_uploaded_list, connected_jobs

def find_connected_jobs(runs, bpmn):
    _nodes = bpmn.__dict__['_BPMN__nodes']
    connected_jobs_list = list()
    for run_key, run_value in runs.items():
        connected_jobs = list()
        for task in run_value:
            for _node in _nodes:
                if _node.id == task.name:
                    node_job_id = JOB.get_job_id_by_task(_node)
            connected_jobs.append(node_job_id)
        connected_jobs_list.append(connected_jobs)

    return connected_jobs_list