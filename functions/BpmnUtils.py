import ast

def parameter_string_to_dict(parameter_str):
    parameter_id, values_str = parameter_str.split(':[')
    values_list = values_str[:-1].split(',')
    return parameter_id, values_list

def transform_annotations(bpmn):
    print()
    print("BpmnUtils ----------------------")
    annotations = bpmn['_BPMN__node_annotations']
    transformed_annotations = {}
    for node_id, parameters in annotations.items():
        command = node_id.name
        parameters_dict = {}
        for parameter in parameters:
            parameter_str = parameter.__dict__['_TextAnnotation__command']
            parameter_id, values_list = parameter_string_to_dict(parameter_str)
            parameters_dict[parameter_id]= values_list
        command_with_values = command
        for key, value in parameters_dict.items():
            command_with_values = command_with_values.replace('$' + key, value[0])
    
    
    return transformed_annotations