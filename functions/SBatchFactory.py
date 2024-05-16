
def create(depend_script, sbatch_file):
    text1 = """#!/usr/local_rwth/bin/zsh\n\n"""
    text2 = ""
    for job_id_script in depend_script:
        text2 += """{}=$(sbatch --parsable {})\n""".format(job_id_script, depend_script[job_id_script])


    sbatch_file.write(text1 + text2)
    