import sys
import os

def parse_files(args):
    number_of_output_files = int(args[-1])
    output_files = args[-number_of_output_files-1:-1] if number_of_output_files > 0 else []
    
    number_of_input_files = int(args[-number_of_output_files-2])
    input_files = args[-number_of_output_files-2-number_of_input_files:-number_of_output_files-2] if number_of_input_files > 0 else []
    
    return input_files, output_files

def parse(script_dir):
    print("-----"*20)
    print("sys.argv: ")
    print(sys.argv)
    
    if int(sys.argv[-1]) == 1:
        output_file = sys.argv[-2]
        number_of_input_files = int(sys.argv[-3])
        start_of_input_files = -number_of_input_files-3
        input_files = sys.argv[start_of_input_files:-3]      
    else:
        output_file = []
        number_of_input_files = int(sys.argv[-2])
        start_of_input_files = -number_of_input_files-2
        input_files = sys.argv[start_of_input_files:-2]

    input_and_output_folder = sys.argv[start_of_input_files-1]
    script_arguments = sys.argv[1:start_of_input_files-1]

    print("output_file: ", output_file)
    print("number_of_input_files: ", number_of_input_files)
    print("input_files: ", input_files)
    print("input_and_output_folder: ", input_and_output_folder)
    print("script_arguments: ", script_arguments)
    inputs_dict = {}

    if len(input_files) > 0:
        for input_file in input_files:
            input_file_path = os.path.join(script_dir, input_file)
            with open(input_file_path, 'r') as file:
                base_name = os.path.splitext(input_file)[0]
                lines = file.readlines()
                lines_dict=dict()
                for line in lines:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    lines_dict[key]=value
                processed_base_name = base_name.split('/')
                inputs_dict[processed_base_name[-1]] = lines_dict
    
    print("inputs_dict: ", inputs_dict)
    print("-----"*20)

    return inputs_dict, output_file, input_and_output_folder, script_arguments

def output_generator(output_file_path, key, value):
    if os.path.exists(output_file_path):
        with open(output_file_path, 'a') as file:
            file.write(f"{key}: {value}\n")
    else:
        with open(output_file_path, 'w') as file:
            file.write(f"{key}: {value}\n")