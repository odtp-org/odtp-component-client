#!/usr/bin/env bash
import yaml
import os
import re
import sys
import logging


def __readTemplate(templatefile):
    """
    :param templatefile: yml file to process
    :return: content of the file as string
    """
    with open(templatefile, 'r') as file:
        content = file.read()
    return content


def __replaceListParameters(content, listPlaceholders, parameterValue):
    """
    :param content: original file content
    :param listPlaceholders:
    :param parameterValue:
    :return: content with replacements of placeholders
    """
    for p, v in zip(listPlaceholders, parameterValue):
            content = content.replace(f"{{{{{p}}}}}", v)
    return content

def __saveConfigFile(content, filepath):
    """
    The content is written to the output file path
    :param content: processed content
    :param filepath: output file path
    :return: output filepath
    """
    with open(filepath, 'w') as file:
        file.write(content)
    return filepath


def __obtainAllPlaceholders(filepath):
    """returns all placeholders in a template file
    :param filepath: input file path
    :return: all placeholders
    """
    template = __readTemplate(filepath)
    pattern = r'\{\{([^{}]+)\}\}'

    # Find all placeholders in the template
    placeholders = re.findall(pattern, template)

    return placeholders


def __process_file(filepath, outputfilepath):
    """
    a file is processed:
    :param filepath: file to process
    :param outputfilepath: output path
    """
    placeholders = __obtainAllPlaceholders(filepath)

    # We expect those values to be in environment
    placeholderValue = []
    placeholders_not_found = []
    for placeholder in placeholders:
        try:
            placeholderValue.append(os.environ[placeholder])
        except Exception as e:
            print(f"{placeholder} not found")
            print(e)
            placeholders_not_found.append(placeholder)
            placeholderValue.append("NotFound")

    # Replacing template
    template = __readTemplate(filepath)
    templateFilled = __replaceListParameters(template, placeholders, placeholderValue)
    outputfilepath = __saveConfigFile(templateFilled, outputfilepath)
    print(f"Output file available: {outputfilepath}.")
    if placeholders_not_found:
        print(f"Some placeholders could not be filled: check your environment "
              f"variables to resolve the errors.")


if __name__ == "__main__":
    # This python script is called from external: it reads a config file and
    # output file path: it replaces all placeholder values marked by {{ .. }}
    # with environment variables of the same name: so {{ HELLO }} is replaced
    # by the value in $HELLO
    print("PREPARATION OF CONFIG FILE")

    if len(sys.argv) < 3:
        print("Please provide a filepath and output filepath as arguments.")
        sys.exit(1)  # Exit the script with an error code

    filepath = sys.argv[1]
    outputfilepath = sys.argv[2]

    __process_file(filepath, outputfilepath)
