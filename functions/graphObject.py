import hashlib
from pm4py.algo.simulation.playout.petri_net.variants import basic_playout
from pm4py.objects.petri_net.obj import PetriNet

class JOB:
    # Class variable to store all instances
    _instances = []

    def __init__(self, task, job_id, application=None, dependency_script=None, input_files=None, output_file=None, srun_file_name=None):
        self.task = task
        self.job_id = job_id
        self.application = application
        self.dependency_script = dependency_script
        self.input_files = input_files
        self.output_file = output_file
        self.srun_file_name = srun_file_name

        # Add the new instance to the class variable list
        JOB._instances.append(self)

    def set_task(self, task):
        self.job_id = task

    def get_task(self):
        return self.task
    
    def set_job_id(self, job_id):
        self.job_id = job_id

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
    
    def set_input_files(self, input_files):
        self.input_files = input_files

    def get_input_files(self):
        return self.input_files
    
    def set_output_file(self, output_file):
        self.output_file = output_file

    def get_output_file(self):
        return self.output_file
    
    def set_srun_file_name(self, srun_file_name):
        self.srun_file_name = srun_file_name

    def get_srun_file_name(self):
        return self.srun_file_name

    @classmethod
    def get_all_jobs(cls):
        return cls._instances
    
    @classmethod
    def set_srun_file_name_by_task(cls, task, new_srun_file_name):
        """Set the srun_file_name value for the job with the given task."""
        for job in cls._instances:
            if job.get_task() == task:
                job.set_srun_file_name(new_srun_file_name)
                return True
        return False
    
    @classmethod
    def set_application_by_task(cls, task, new_application):
        """Set the application value for the job with the given job_id."""
        for job in cls._instances:
            if job.get_task() == task:
                job.set_application(new_application)
                return True
        return False
    
    @classmethod
    def set_dependency_script_by_job_id(cls, job_id, new_dependency_script):
        """Set the dependency_script value for the job with the given job_id."""
        for job in cls._instances:
            if job.get_job_id() == job_id:
                job.set_dependency_script(new_dependency_script)
                return True
        return False

    @classmethod
    def set_input_files_by_job_id(cls, job_id, new_input_files):
        """Set the input_files value for the job with the given job_id."""
        for job in cls._instances:
            if job.get_job_id() == job_id:
                job.set_input_files(new_input_files)
                return True
        return False

    @classmethod
    def set_output_file_by_job_id(cls, job_id, new_output_file):
        """Set the output_file value for the job with the given job_id."""
        for job in cls._instances:
            if job.get_job_id() == job_id:
                job.set_output_file(new_output_file)
                return True
        return False
    
    @classmethod
    def get_task_by_job_id(cls, job_id):
        """Return the task associated with the given job_id."""
        for job in cls._instances:
            if job.get_job_id() == job_id:
                return job.task
        return None

    @classmethod
    def get_job_id_by_task(cls, task):
        """Return the job_id associated with the given task."""
        for job in cls._instances:
            if job.task == task:
                return job.get_job_id()
        return None

def hash_to_4_digit_number(input_string):
    hashed = hashlib.sha256(input_string.encode()).hexdigest()
    first_4_chars = hashed[:4]
    decimal_number = int(first_4_chars, 16)
    four_digit_number = decimal_number % 10000
    
    return four_digit_number
def get_unique_number_added_to_job_id(task):
    task_name = task.name
    task_name1 = task_name.replace(" ", "_")
    return str(hash_to_4_digit_number(task_name1))

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

def get_job_application_from_label(task):
    task_label = task.label
    command = task_label.split('.')[0] if '.' in task_label else task_label
    return command.strip()

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

def get_transition(net, node):
    for tran in net.transitions:
        if tran.label == node:
            return tran
        else:
            continue

def runs_and_inputs_factory(net, im, fm):
    runs = find_runs(net, im, fm)
    all_inputs_dict = {}
    for index, run in runs.items():
        inputs_dict = inputs(net, run)
        all_inputs_dict[index] = inputs_dict
        # dag = storageprocessor.create_dag(edges)
        # storageprocessor.save_dag(dag)

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

def add_dependency(task, run_inputs, depend_script, job_ids, processed_tasks, j_dep_list, should_be_uploaded_list):
    # based on the name of the application needs to be run on SLURM and the task id we generate a unique a name for our bash file
    # that contains srun and parameter settings
    srun_file_name = get_unique_number_added_to_job_id(task) + "_" + get_job_application_from_label(task) + '.sh'
    JOB.set_srun_file_name_by_task(task, srun_file_name)
    command = get_command_from_label(task)
    JOB.set_application_by_task(task, command)
    # SRunFactory_new.create(srun_file_name, application, should_be_uploaded_list)
    # we also need a job id that refers to srun file in our sbatch file

    job_id = 'job_id_' + str(get_unique_number_added_to_job_id(task))

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

    for data_object in _BPMN__data_objects:
        data_object_details = _BPMN__data_objects[data_object]
        source_ref_id = data_object_details['source_ref']
        target_ref_id = data_object_details['target_ref']
        

def create(petri_net, im, fm, bpmn):
    transitions = petri_net.transitions
    for transition in transitions:
        job_id = 'job_id_' + str(get_unique_number_added_to_job_id(transition))
        JOB(task=transition, job_id=job_id)

    runs, all_inputs_dict = runs_and_inputs_factory(petri_net, im, fm)
    depend_script, should_be_uploaded_list = dependency_script_factory(runs, all_inputs_dict)
    for job_id_dep in depend_script:
        JOB.set_dependency_script_by_job_id(job_id_dep, depend_script[job_id_dep])

    #TODO: STARTPOINT
    output_and_input_files_factory(bpmn)
    

    print()
    print()
    print()
    for job in JOB.get_all_jobs():
        print(f"Task: {job.get_task()},      Job ID: {job.get_job_id()},      Application: {job.get_application()}") 
        print(f"Dependency Script: {job.get_dependency_script()},       Input Files: {job.get_input_files()}")
        print(f"Output File: {job.get_output_file()},           SRun File Name: {job.get_srun_file_name()}")
    print()
    print()
    print()