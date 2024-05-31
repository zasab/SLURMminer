import pm4py
#-------------------------------------------------
import os, sys
from os.path import dirname, abspath
filedir = dirname(abspath(__file__))
basedir = dirname(dirname(abspath(__file__)))
sys.path.insert(1, basedir)
import command_parser

script_dir = os.path.dirname(os.path.abspath(__file__))
inputs_dict, output_file, script_arguments = command_parser.parse(script_dir)
print("inputs_dict: ", inputs_dict)
print("output_file: ", output_file)
print("script_arguments: ", script_arguments)
print()
# #-------------------------------------------------

log = pm4py.read_xes(inputs_dict['log_info'])
net, im, fm = pm4py.discover_petri_net_inductive(log)
fitness_token_based_replay = pm4py.fitness_token_based_replay(log, net, im, fm)
fitness_alignments = pm4py.fitness_alignments(log, net, im, fm)

print("fitness_token_based_replay: ", fitness_token_based_replay)
print("fitness_alignments: ", fitness_alignments)