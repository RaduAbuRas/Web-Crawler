#Class that contains utility methods

def compute_alpha_numerical_string(string):
    # Strip string of /n and /t tags from beginning and end
    string = string.rstrip().strip()

    # Remove non alphanumerical characters in string
    alpha_num_string = "".join([x if x.isalnum() else "_" for x in string])
    
    return alpha_num_string