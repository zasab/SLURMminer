import pm4py
from pm4py.visualization.petri_net import visualizer as pn_visualizer
import warnings
warnings.filterwarnings("ignore")
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

with open('new_file.txt', 'r') as file:
    file_path = file.read()

log = pm4py.read_xes(file_path)
net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log)
parameters = {pn_visualizer.Variants.FREQUENCY.value.Parameters.FORMAT: "png"}
gviz = pn_visualizer.apply(net, initial_marking, final_marking, parameters=parameters, variant=pn_visualizer.Variants.FREQUENCY, log=log)

model_path = file_path = os.path.join(script_dir, "inductive_frequency.png")
pn_visualizer.save(gviz, model_path)