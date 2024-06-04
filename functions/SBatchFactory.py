import random
import string
from functions.graphObject import JOB

# def create2(depend_script, sbatch_file, CI):
#     text1 = """#!/bin/bash\n\n"""
#     text1 += 'FILES_DIR=$(echo $RANDOM | md5sum | head -c 8)\n'
#     text1 += 'FILES_DIR="{}_$FILES_DIR"\n'.format(CI)
#     text1 += 'mkdir $FILES_DIR\n'
#     text2 = ""
    
#     for job_id_script in depend_script:
#         output_file = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
#         text2 += """{}=$(sbatch --parsable {} $FILES_DIR)\n""".format(job_id_script, depend_script[job_id_script])

#         for job in JOB.get_all_jobs():
#             print(job.get_job_id())
#             print(job.get_dependency_script())


#     sbatch_file.write(text1 + text2)


def create(sbatch_file, connected_jobs, main_CI):
    text1 = """#!/bin/bash\n\n"""
    text1 += 'FILES_DIR=$(echo $RANDOM | md5sum | head -c 4)\n'
    text1 += 'FILES_DIR="{}_$FILES_DIR"\n'.format(main_CI)
    # text1 += 'mkdir $FILES_DIR\n'
    text2 = ""

    for job in JOB.get_all_jobs():
        for connected_job in connected_jobs:
            if job.get_job_id() in connected_job:
                CI = '_'.join(connected_job)
        text2 += """{}=$(sbatch --parsable {} $FILES_DIR {})\n""".format(job.get_job_id(), job.get_dependency_script(), CI)


    sbatch_file.write(text1 + text2)
    