from functions import BpmnUtils
import config


def srun_file_content(srun_file, srun_file_name, command, REMOTE_PATH_HOME_FILE, REMOTE_FOLDER_NAME):
    text1 = """#!/usr/local_rwth/bin/zsh

# Runtime and memory
#SBATCH --mem-per-cpu=6G

# For parallel jobs
#SBATCH --cpus-per-task=16
#SBATCH --nodes=2
#SBATCH --ntasks=2
#SBATCH --ntasks-per-node=1
#SBATCH --output={0}_res_%j.txt

#### Your shell commands below this line ####

export LD_LIBRARY_PATH="/usr/local_rwth/sw/python/3.8.7/x86_64/lib/:${{LD_LIBRARY_PATH}}"
srun {1}/{2}/wrap_time.sh /usr/local_rwth/sw/python/3.8.7/x86_64/bin/python3.8 {3}
""".format(srun_file_name[:-3], REMOTE_PATH_HOME_FILE, REMOTE_FOLDER_NAME, command)
    
    text2 = """
if [ $? -eq 0 ]; then
    echo "0" >> "file1_${SLURM_JOB_ID}.txt"
    exit 0
else
    echo "1" >> "file2_${SLURM_JOB_ID}.txt"
    exit 1
fi
"""

    srun_file.write(text1 + text2)

def create(srun_file_name, command, should_be_uploaded_list):
    srun_file_path = "{}/{}".format(config.bpmn.uploaded_files_directory, srun_file_name)
    should_be_uploaded_list.add(srun_file_path)
    srun_file = open(srun_file_path, 'w')
    srun_file_content(srun_file, srun_file_name, command, 'TODO', 'TODO')