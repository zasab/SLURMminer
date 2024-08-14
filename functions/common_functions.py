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


def hash_to_5_digit_string(input_string):
    # Use SHA-256 hash function for the input string
    hash_object = hashlib.sha256(input_string.encode())
    # Convert the hash to an integer
    hash_int = int(hash_object.hexdigest(), 16)
    # Get a number in the range 0 to 99999
    five_digit_number = hash_int % 100000
    # Convert the number to a 5-digit string, padding with leading zeros if necessary
    five_digit_string = f"{five_digit_number:05d}"
    return five_digit_string

def generate_unique_hash(input_string):
    # Get the hash of the input string
    hash_value = hash(input_string)
    # Convert the hash to a hexadecimal string
    hex_hash = hex(hash_value)
    # Truncate the hexadecimal string to 5 characters
    truncated_hash = hex_hash[2:7]  # Remove '0x' prefix and take first 5 characters
    return truncated_hash