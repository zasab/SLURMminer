python.exe .\import_log.py 'running-example.xes' hhh 0 hhh/log_info.txt 1
python.exe .\inductive_miner.py 0.4 hhh hhh/log_info.txt 1 hhh/model_info.txt 1
python.exe .\alignments.py hhh hhh/model_info.txt hhh/log_info.txt 2 hhh/alignments_fitness.txt 1
python.exe .\token_based_replay.py hhh hhh/model_info.txt hhh/log_info.txt 2 hhh/token_based_fitness.txt 1