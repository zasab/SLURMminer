import sys
import os

def parse_files(args):
    number_of_output_files = int(args[-1])
    output_files = args[-number_of_output_files-1:-1] if number_of_output_files > 0 else []
    
    number_of_input_files = int(args[-number_of_output_files-2])
    input_files = args[-number_of_output_files-2-number_of_input_files:-number_of_output_files-2] if number_of_input_files > 0 else []
    
    return input_files, output_files

def parse(script_dir):
    input_files, output_files = parse_files(sys.argv)
    if len(output_files) > 0:
        output_file = output_files[0]
    else:
        output_file = ''

    inputs_dict = {}
    if len(input_files) > 0:
        for input_file in input_files:
            input_file_path = os.path.join(script_dir, input_file)
            with open(input_file_path, 'r') as file:
                content = file.readline().strip()
                base_name = os.path.splitext(input_file)[0]
                print()
                print("base_name: ", base_name)
                print()
                processed_base_name = base_name.split('/')
                print("processed_base_name: ", processed_base_name)
                inputs_dict[processed_base_name[-1]] = content

    end_of_arguments = len(input_files) + 3
    script_arguments = sys.argv[1:-end_of_arguments]

    return inputs_dict, output_file, script_arguments

def output_generator(output_file_path, new_output):
    with open(output_file_path, 'w') as file:
        file.write(f"{new_output}\n")