import random
import string


def create(depend_script, sbatch_file):
    text1 = """#!/usr/local_rwth/bin/zsh\n\n"""
    text2 = ""
    
    for job_id_script in depend_script:
        print()
        print()
        print()
        output_file = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        print("output_file: ", output_file)
        print("depend_script[job_id_script]: ", depend_script[job_id_script])
        text2 += """{}=$(sbatch --parsable {})\n""".format(job_id_script, depend_script[job_id_script])


    sbatch_file.write(text1 + text2)
    