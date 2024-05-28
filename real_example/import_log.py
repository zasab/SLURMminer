import os
import warnings
warnings.filterwarnings("ignore")
import sys

if len(sys.argv) < 2:
    print("Give the log as input argument after", sys.argv[0])
    sys.exit(1)

script_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(script_dir, 'logs', sys.argv[1])

with open('log_path.txt', 'w') as file:
    file.write("log_path\n")