import os
file_path = "DependScriptGen.sh"
os.remove(file_path)
if os.path.exists(file_path):
    pass
else:
    try:
        with open(file_path, "w") as file:
            print("Content written to new file.")
    except Exception as e:
        print(f"An error occurred while creating and writing to the file: {e}")

job_ids = {}
job_scripts = {}

def generate_dependency_script(runs, inputs):
    processedTasks = []
    oldInputs = {}
    old_deps = ""
    for run in runs:
        tasks = topological_sort(inputs[run])
        inputs_r = inputs[run]
        for task in tasks:
            if task not in job_scripts:
                set_lambda_F_JS(task)
            f_a = get_F_JS(task)
            if task not in job_ids:
                set_lambda_job_id(task)
            j_a = get_job_id(task)
            if task not in processedTasks:
                processedTasks.append(task)
                in_task = list(inputs_r[task])
                if len(in_task) == 0:
                    dep = ""
                    with open(file_path, "a") as file:
                        file.write("{}={}\n".format(j_a, f_a))
                elif len(in_task) == 1:
                    y = in_task[0]
                    j_y = get_job_id(y)
                    with open(file_path, "a") as file:
                        dep = f"{j_y}"
                        file.write(f"{j_a}=--dependency=afterok:(${dep}) {f_a}\n")
                elif len(in_task) > 1:
                    y_i = [in_task[i] for i in range(len(in_task))]
                    j_y_i = [get_job_id(y_i[i]) for i in range(len(in_task))]
                    with open(file_path, "a") as file:
                        dep = f"{','.join(j_y_i)}"
                        file.write(f"{j_a}=--dependency=afterok:(${dep}) {f_a}\n")

                if task in oldInputs:
                    oldInputs[task] += in_task
                else:
                    oldInputs[task] = in_task
            else:
                newInputs = list(inputs_r[task])
                if not set(newInputs).issubset(oldInputs[task]):
                    j_z_i = [get_job_id(oldInputs[task][i]) for i in range(len(oldInputs[task]))]
                    if len( j_z_i) > 1:
                        old_deps += f"({','.join(j_z_i)}),"
                    else:
                        old_deps += f"{','.join(j_z_i)},"
                    j_y_i = [get_job_id(newInputs[i]) for i in range(len(newInputs))]
                    if len( j_y_i) > 1:
                        new_deps = f"({','.join(j_y_i)}),"
                    else:
                        new_deps = f"{','.join(j_y_i)},"
                    remove_previous_deps(file_path, f"{j_a}=--dependency:")
                    with open(file_path, "a") as file:
                        dep = f"{old_deps}{new_deps}"
                        file.write(f"{j_a}=--dependency:afterany({dep[:-1]}) {f_a}\n")
                    oldInputs[task] += newInputs
                else:
                    continue


def topological_sort(dependencies):
    # Initialize an empty dictionary to represent the graph
    graph = {}

    # Populate the graph with tasks and their dependencies
    for task, deps in dependencies.items():
        if task not in graph:
            graph[task] = set()
        for dep in deps:
            graph[task].add(dep)

    # Initialize a dictionary to store the in-degree of each task
    in_degree = {task: 0 for task in graph}
    for dependencies in graph.values():
        for dependency in dependencies:
            in_degree[dependency] += 1

    # Initialize an empty list to store the sorted tasks
    sorted_tasks = []

    # Perform topological sort using Kahn's algorithm
    queue = [task for task in in_degree if in_degree[task] == 0]
    while queue:
        current_task = queue.pop(0)
        sorted_tasks.append(current_task)
        for dependent_task in graph.get(current_task, []):
            in_degree[dependent_task] -= 1
            if in_degree[dependent_task] == 0:
                queue.append(dependent_task)

    # Check for cycles
    if len(sorted_tasks) != len(graph):
        raise ValueError("Graph contains a cycle")

    return sorted_tasks[::-1]

def set_lambda_F_JS(task):
    job_scripts[task] = 'file_____{0}'.format(task)

def get_F_JS(task):
    return job_scripts[task]

def set_lambda_job_id(task):
    job_ids[task] = 'job_id____{0}'.format(task)

def get_job_id(task):
    return job_ids[task]

def remove_previous_deps(file_path, target_line):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()

        with open(file_path, "w") as file:
            for line in lines:
                if not line.startswith(target_line):
                    file.write(line)
    except FileNotFoundError:
        print(f"The file '{file_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    runs = {"run1": {"a", "b", "c", "d", "f", "g"}, "run2": {"f", "g"}}
    inputs = {
        "run1": {"a": {}, "f": {}, "b": {"a", "f"}, "c": {"a"}, "d": {"b", "c"}, "g": {"b"}},
        "run2": {"f": {}, "g": {"f"}},
    }
    generate_dependency_script(runs, inputs)

if __name__ == "__main__":
    main()
