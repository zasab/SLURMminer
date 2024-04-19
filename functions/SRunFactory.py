from functions import BpmnUtils

def srun_file_content(srun_filename, srun_command, res_file_name, REMOTE_FOLDER_NAME, REMOTE_PATH_HOME_FILE):
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
srun {1}/{2}/wrap_time.sh /usr/local_rwth/sw/python/3.8.7/x86_64/bin/python3.8 {3} "$@"
""".format(res_file_name, REMOTE_PATH_HOME_FILE, REMOTE_FOLDER_NAME, srun_command.split(' ')[0])
    
    text2 = """
if [ $? -eq 0 ]; then
    echo "0" >> "file1_${SLURM_JOB_ID}.txt"
    exit 0
else
    echo "1" >> "file2_${SLURM_JOB_ID}.txt"
    exit 1
fi
"""

    srun_filename.write(text1 + text2)

def create(processed_bpmn):
    print()
    print("SRunFactory -------------------")
    activity_belongings = BpmnUtils.transform_annotations(processed_bpmn.__dict__)
    # print(activity_belongings)
    print()
    # 
    # for task, task_features in activity_belongings.items():
    #     srun_file_path = "{}/{}.sh".format(BPMN_directory, task_features['srun_filename'])
    #     srun_file = open(srun_file_path, 'w')
    #     should_be_uploaded_list.append(srun_file_path)
    #     res_file_name = str(task_features['srun_filename'])
    #     srun_file_content(srun_file, task_features['srun_command'], res_file_name, REMOTE_FOLDER_NAME, REMOTE_PATH_HOME_FILE)