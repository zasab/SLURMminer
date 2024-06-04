import hashlib

def hash_to_4_digit_number(input_string):
    hashed = hashlib.sha256(input_string.encode()).hexdigest()
    first_4_chars = hashed[:4]
    decimal_number = int(first_4_chars, 16)
    four_digit_number = decimal_number % 10000
    
    return four_digit_number

def get_unique_number_added_to_job_id(task):
    task_name = task.name
    task_name1 = task_name.replace(" ", "_")
    return str(hash_to_4_digit_number(task_name1)) 