import pm4py
from pm4py.visualization.petri_net import visualizer as pn_visualizer
import warnings
warnings.filterwarnings("ignore")

#-------------------------------------------------
import os, sys
from os.path import dirname, abspath
filedir = dirname(abspath(__file__))
basedir = dirname(dirname(abspath(__file__)))
sys.path.insert(1, basedir)
import command_parser

script_dir = os.path.dirname(os.path.abspath(__file__))
inputs_dict, output_file, input_and_output_folder, script_arguments = command_parser.parse(script_dir)
#-------------------------------------------------

log_path = inputs_dict['log_info']['log_path']
noise_threshold = float(script_arguments[0])
log = pm4py.read_xes(log_path)
net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log, noise_threshold=noise_threshold)
parameters = {pn_visualizer.Variants.FREQUENCY.value.Parameters.FORMAT: "png"}
gviz = pn_visualizer.apply(net, initial_marking, final_marking, parameters=parameters, variant=pn_visualizer.Variants.FREQUENCY, log=log)
model_path = os.path.join(script_dir, input_and_output_folder, f"inductive_frequency_{noise_threshold}_{os.path.basename(log_path).split('.')[0]}.png")
pn_visualizer.save(gviz, model_path)

#------------------------------------------------- outputs
if output_file:
    command_parser.output_generator(os.path.join(script_dir, output_file), "model_path", model_path)
    command_parser.output_generator(os.path.join(script_dir, output_file), "noise_threshold", noise_threshold)



