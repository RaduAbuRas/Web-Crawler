#Class that contains utility methods

def computeAlphaNumericalString(string):
    # Strip string of /n and /t tags from beginning and end
    string = string.rstrip().strip()

    # Remove non alphanumerical characters in string
    alphaNumString = "".join([x if x.isalnum() else "_" for x in string])
    
    return alphaNumString