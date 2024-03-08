import yaml
import os
import re
import sys

def readTemplate(templatefile):

    with open(templatefile, 'r') as file:
        content = file.read()

    return content

def replaceListParameters(content, listPlaceholders, parameterValue):

    for p, v in zip(listPlaceholders, parameterValue):
            content = content.replace(f"[{p}]", v)

    return content

def saveConfigFile(content, filepath):

    with open(filepath, 'w') as file:
        file.write(content)

    return filepath

def readODTPConfigYAML(configfile):
    with open(configfile, 'r') as file:
        data = yaml.safe_load(file)
     
    return data

def obtainAllPlaceholders(filepath):
    template = readTemplate(filepath)

    pattern = r'\[([^[\]]+)\]'

    # Find all placeholders in the template
    placeholders = re.findall(pattern, template)

    return placeholders

     

if __name__ == "__main__":

    print("PREPARATION OF CONFIG FILE")

    if len(sys.argv) < 3:
        print("Please provide a filepath and output filepaht as arguments.")
        sys.exit(1)  # Exit the script with an error code

    filepath = sys.argv[1]
    outputfilepath = sys.argv[2]

    odtpConfig = readODTPConfigYAML("/odtp/odtp-config/odtp.yml")
    #argumentsdefault = odtpConfig["arguments"]
    #Take the default from here

    # Implementing simple load of parameters by now. Not based in the odtp config file, as both pipelines contains different arguments name. 
    placeholders = obtainAllPlaceholders(filepath)

    # We expect those values to be in environment
    placeholderValue = []
    for placeholder in placeholders:
        try:
            placeholderValue.append(os.environ[placeholder])
        except Exception as e:
            print(f"{placeholder} not found")
            print(e)


    # Replacing template
    template = readTemplate(filepath)
    templateFilled = replaceListParameters(template, placeholders, placeholderValue)
    _ = saveConfigFile(templateFilled, outputfilepath)

    print("PREPARATION OF CONFIG DONE")




