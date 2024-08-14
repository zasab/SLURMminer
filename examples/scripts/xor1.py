import warnings
warnings.filterwarnings("ignore")
import sys

#-------------------------------------------------
import os, sys
from os.path import dirname, abspath
filedir = dirname(abspath(__file__))
basedir = dirname(dirname(abspath(__file__)))
sys.path.insert(1, basedir)
import command_parser

script_dir = os.path.dirname(os.path.abspath(__file__))
inputs_dict, output_file, input_and_output_folder, script_arguments = command_parser.parse(script_dir)
# #-------------------------------------------------

log_path = inputs_dict['log_info']['log_path']
if 'BPI_Challenge_2013_open_problems.xes' in log_path or 'running-example.xes' in log_path:
    #------------------------------------------------- outputs
    if output_file:
        command_parser.output_generator(os.path.join(script_dir, output_file), 
                                        'for BPI_Challenge_2013_open_problems.xes or running-example.xes successfully pass to next task.......... ')

    print('for BPI_Challenge_2013_open_problems.xes or running-example.xes successfully pass to next task.......... ')
    sys.exit(0)
else:
    #------------------------------------------------- outputs
    if output_file:
        command_parser.output_generator(os.path.join(script_dir, output_file), 'for BPIC15_4.xes exit code 1 ...........')

    print('for BPIC15_4.xes exit code 1 ...........')
    sys.exit(1)
