import pm4py
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
noise_threshold = float(inputs_dict['model_info1']['noise_threshold'])
log = pm4py.read_xes(log_path)
net, im, fm = pm4py.discover_petri_net_inductive(log, noise_threshold=noise_threshold)
fitness_alignments = pm4py.fitness_alignments(log, net, im, fm)
#------------------------------------------------- outputs
if output_file:
    command_parser.output_generator(os.path.join(script_dir, output_file), "fitness_alignments", fitness_alignments)
