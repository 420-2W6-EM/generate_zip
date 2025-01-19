import os
import re
import json
import subprocess
import argparse

def load_configuration(config_path):
    with open(config_path, 'r', encoding='utf-8') as config_file:
        return json.load(config_file)

def process_file(file_path, delete_expressions, add_expressions, version):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    if version == 'versiondepart':

        for expression in delete_expressions:
            content = apply_expression_rule_1(content, expression)
            content = apply_expression_rule_2(content, expression)
        next

        for expression in add_expressions:
            content = apply_expression_rule_3(content, expression)
            content = apply_expression_rule_4(content, expression)
        next

    if version == 'versionsolution':

        for expression in delete_expressions:
            print(expression)
            content = apply_expression_rule_3(content, expression)
            content = apply_expression_rule_4(content, expression)
        next

        for expression in add_expressions:
            content = apply_expression_rule_1(content, expression)
            content = apply_expression_rule_2(content, expression)
        next
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def apply_expression_rule_1(content, expression):
    """
    Transformation #1

    AVANT:
        [EXPRESSION_START]
        <meta charset="UTF-8">
        <title>ne pas afficher dans la version de départ</title>
        [EXPRESSION_FIN]

    APRÈS:
        rien...

    RÈGLES:
        - Il faut que le tag de début et de fin soient sur des lignes différentes.
        - Il doit y avoir rien d'autres sur les 2 lignes que les tags de début et de fin (sauf des espaces ou tabulations).
    """
    start_pattern = expression['start']
    end_pattern = expression['end']
    result = []
    lines = content.split('\n')
    skip = False
    for line in lines:
        if line.strip() == start_pattern:
            skip = True
        if not skip:
            result.append(line)
        if line.strip() == end_pattern:
            skip = False
    return '\n'.join(result)


def apply_expression_rule_2(content, expression):
    """
    Transformation #2 

    AVANT:
        <meta charset="UTF-8">[EXPRESSION_START]<h1>ne pas afficher dans version départ</h1>[EXPRESSION_FIN]

    APRÈS:
        <meta charset="UTF-8">

    RÈGLES :
        - Il faut que le tag de début et de fin soit sur la même ligne.
        - Il faut qu'il y aille d'autres caractères que les tags de début et de fin sur la ligne (ex ici : <meta charset="UTF-8">).
    """
    start_pattern = expression['start']
    end_pattern = expression['end']
    lines = content.split('\n')
    result = []
    for line in lines:
        trimmed_line = line.strip()
        if start_pattern in trimmed_line and end_pattern in trimmed_line:
            before_start = trimmed_line.split(start_pattern)[0]
            after_end = trimmed_line.split(end_pattern)[1]
            if before_start.strip() or after_end.strip():
                line = line.replace(trimmed_line, before_start + after_end)
        result.append(line)
    return '\n'.join(result)

def apply_expression_rule_3(content, expression):
    """
    Transformation #3
    
    AVANT:
        [EXPRESSION_START]
        <meta charset="UTF-8">
        <title>Titre provisoire</title>
        [EXPRESSION_END]
    
    APRÈS:
        <meta charset="UTF-8">
        <title>Titre provisoire</title>
    
     
    RÈGLES :
        - Il faut que le tag de début et de fin soient sur des lignes différentes.
        - Il doit y avoir rien d'autres sur les 2 lignes que les tags de début et de fin (sauf des espaces ou tabulations).
    """
    start_pattern = expression['start']
    end_pattern = expression['end']
    result = []
    lines = content.split('\n')
    for line in lines:
        if line.strip() == start_pattern:
            continue
        if line.strip() == end_pattern:
            continue
        result.append(line)
    return '\n'.join(result)


def apply_expression_rule_4(content, expression):
    """
    Transformation #4

    AVANT:
        <meta charset="UTF-8">[EXPRESSION_START]<h1>afficher dans version départ, mais pas dans la version solution</h1>[EXPRESSION_END]

    APRÈS:
        <meta charset="UTF-8"><h1>afficher dans version départ, mais pas dans la version solution</h1>

    RÈGLES :
        - Il faut que le tag de début et de fin soit sur la même ligne.
        - Il faut qu'il y aille d'autres caractères que les tags de début et de fin sur la ligne (ex ici : <meta charset="UTF-8">).
    """
    start_pattern = expression['start']
    end_pattern = expression['end']
    lines = content.split('\n')
    result = []
    for line in lines:
        trimmed_line = line.strip()
        if start_pattern in trimmed_line and end_pattern in trimmed_line:
            line = line.replace(start_pattern, "")
            line = line.replace(end_pattern, "")
        result.append(line)
    return '\n'.join(result)

def process_directory(directory, config, version):
    delete_expressions = config['deleteStartVersionExpressions']
    add_expressions = config['addInStartVersionExpressions']
    extensions = config['extensions']

    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                subprocess.run(["dos2unix", file_path]) # Convert file to Unix format, otherwise some lines may not be transform correctly
                process_file(file_path, delete_expressions, add_expressions, version)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process files for start version.')
    parser.add_argument('directory', help='Directory to process')
    parser.add_argument('-c', '--config', default='configuration-start-version.json', help='Path to the configuration file')
    parser.add_argument('-v', '--version', default='versiondepart', choices=['versiondepart', 'versionsolution'], help='Version to process (default: versiondepart)')
    args = parser.parse_args()

    directory = args.directory
    config_path = args.config
    version = args.version

    config = load_configuration(config_path)
    process_directory(directory, config, version)