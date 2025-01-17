import os
import re
import json

def load_configuration(config_path):
    with open(config_path, 'r', encoding='utf-8') as config_file:
        return json.load(config_file)

def process_file(file_path, delete_expressions, add_expressions):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    content = apply_delete_expressions(content, delete_expressions)
    content = apply_add_expressions(content, add_expressions)

    # Remove lines that are empty or contain only spaces/tabs
    content = re.sub(r'^\s*$', '', content, flags=re.MULTILINE)

    # Remove any remaining empty lines
    content = os.linesep.join([s for s in content.splitlines() if s.strip()])

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def apply_delete_expressions(content, delete_expressions):
    for expression in delete_expressions:
        pattern = re.escape(expression['start']) + r'.*?' + re.escape(expression['end'])
        content = re.sub(pattern, '', content, flags=re.DOTALL)
        # Remove lines containing start and end expressions
        content = re.sub(r'^.*' + re.escape(expression['start']) + r'.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'^.*' + re.escape(expression['end']) + r'.*$', '', content, flags=re.MULTILINE)
    return content

def apply_add_expressions(content, add_expressions):
    for expression in add_expressions:
        # Remove the start tag
        content = re.sub(re.escape(expression['start']), '', content)
        # Remove the end tag
        content = re.sub(re.escape(expression['end']), '', content)
    return content

def process_directory(directory, config):
    delete_expressions = config['deleteStartVersionExpressions']
    add_expressions = config['addInStartVersionExpressions']
    extensions = config['extensions']

    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                process_file(file_path, delete_expressions, add_expressions)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python process_files.py <directory> <config_path>")
        sys.exit(1)

    directory = sys.argv[1]
    config_path = sys.argv[2]

    config = load_configuration(config_path)
    process_directory(directory, config)