from functions.graphObject import JOB
import hashlib
from functions import common_functions

import re

def extract_job_ids(input_string):
    # Regular expression to match job IDs
    job_id_pattern = r'\bjob_id_\d+\b'
    # Find all occurrences of the pattern
    job_ids = re.findall(job_id_pattern, input_string)
    return job_ids

def add_dependencies(job_id, dependecies, connected_jobs, sorted_job_id_dependecies):
    for dependecy in dependecies:
        if dependecy in connected_jobs:
            connected_jobs[dependecy].add(job_id)
        else:
            for job_id_key, dep_values in connected_jobs.items():
                if dependecy in dep_values:
                    connected_jobs[job_id_key].add(job_id)
                
            # add_dependencies(dependecy, dependecy_dependecies, connected_jobs, sorted_job_id_dependecies)
    
    return connected_jobs

def find_related_ones():
    job_id_dependecies = {}
    connected_jobs = {}
    for job in JOB.get_all_jobs():
        job_id_dependecies[job.get_job_id()] = extract_job_ids(job.get_dependency_script())

    sorted_job_id_dependecies = dict(sorted(job_id_dependecies.items(), key=lambda item: len(item[1])))

    for job_id in sorted_job_id_dependecies:
        dependecies = sorted_job_id_dependecies[job_id]
        if len(dependecies) == 0:
            connected_jobs[job_id] = set()
            connected_jobs[job_id].add(job_id)
        else:
            add_dependencies(job_id, dependecies, connected_jobs, sorted_job_id_dependecies)
    
    connected_jobs_list = list()
    for connected_job_key in connected_jobs:
        connected_jobs_list.append(list(connected_jobs[connected_job_key]))

    return connected_jobs_list

def create(sbatch_file, main_CI):
    text1 = """#!/bin/bash\n\n"""
    text1 += 'FILES_DIR=$(echo $RANDOM | md5sum | head -c 4)\n'
    text1 += 'FILES_DIR="{}_$FILES_DIR"\n'.format(main_CI)
    # text1 += 'mkdir $FILES_DIR\n'
    text2 = ""
    
    connected_jobs_list = find_related_ones()

    for job in JOB.get_all_jobs():
        for connected_job in connected_jobs_list:
            if job.get_job_id() in connected_job:
                all_connected_jobs = '_'.join(connected_job)
                CI = common_functions.hash_to_5_digit_string(all_connected_jobs)
        text2 += """{}=$(sbatch --parsable {} $FILES_DIR {})\n""".format(job.get_job_id(), job.get_dependency_script(), CI)


    sbatch_file.write(text1 + text2)
    