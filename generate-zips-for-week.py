import json
import os
import shutil
import zipfile
import subprocess
from git import Repo


# Constante globale pour le répertoire des fichiers supplémentaires
SUPPLEMENTARY_FILES_DIR = 'files-to-include-in-zip'

def load_config(file_path):
    """
    Charge le fichier de configuration JSON.
    
    :param file_path: Chemin vers le fichier JSON.
    :return: Dictionnaire contenant la configuration.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def apply_global_config(config, global_config):
    """
    Applique la configuration globale à la configuration spécifique d'un item.
    
    :param config: Configuration spécifique de l'item.
    :param global_config: Configuration globale à appliquer.
    """
    for key in global_config:
        if key in config:
            config[key].extend(global_config[key])
        else:
            config[key] = global_config[key]

def add_files(base_path, config):
    """
    Prépare le répertoire en ajoutant les fichiers spécifiés.
    
    :param base_path: Chemin de base du répertoire.
    :param config: Configuration de l'item.
    """
    os.makedirs(base_path, exist_ok=True)
    for file_info in config.get(f'FichiersRajouter', []):
        src_file = os.path.join(SUPPLEMENTARY_FILES_DIR, file_info['source_full_file_path'])
        if 'destination_folder_path' in file_info :
            destination_directory = os.path.join(base_path, file_info['destination_folder_path'])    
            if not os.path.exists(destination_directory):
                os.makedirs(destination_directory)
        else:
            destination_directory = base_path
        dest_file = os.path.join(destination_directory, file_info['destination_filename'])
        os.makedirs(destination_directory, exist_ok=True)
        if os.path.exists(src_file):
            shutil.copy(src_file, dest_file)

def add_files_root_zip(base_path, config, section, version):
    """
    Prépare le répertoire en ajoutant les fichiers spécifiés à la racine du ZIP.
    
    :param base_path: Chemin de base du répertoire.
    :param config: Configuration de l'item.
    """
    for file_info in config.get(f'FichiersRajouterRacineZip', []):
        if section+version in file_info['versions'] :
            src_file = os.path.join(SUPPLEMENTARY_FILES_DIR, file_info['source_full_file_path'])
            dest_file = os.path.join(base_path, file_info['destination_filename'])
            if os.path.exists(src_file):
                shutil.copy(src_file, dest_file)


def remove_files(base_path, config, version):
    """
    Supprime les fichiers spécifiés dans la configuration.
    
    :param base_path: Chemin de base du répertoire.
    :param config: Configuration de l'item.
    :param version: Version ('' pour générale, 'VersionDepart' ou 'VersionSolution').
    """
    for file in config.get(f'FichiersSupprimer{version}', []):
        file_path = os.path.join(base_path, file)
        if os.path.exists(file_path):
            os.remove(file_path)

def remove_directories(base_path, config, version):
    """
    Supprime les dossiers spécifiés dans la configuration.
    
    :param base_path: Chemin de base du répertoire.
    :param config: Configuration de l'item.
    :param version: Version ('' pour générale, 'VersionDepart' ou 'VersionSolution').
    """
    for directory in config.get(f'DossiersSupprimer{version}', []):
        dir_path = os.path.join(base_path, directory)
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)

def process_items(items, global_config, base_dir, version):
    """
    Traite chaque item (exemple ou exercice) en appliquant les configurations et en préparant les fichiers.
    
    :param items: Liste des items à traiter.
    :param global_config: Configuration globale à appliquer.
    :param base_dir: Répertoire de base pour les fichiers.
    :param version: Version ('VersionDepart' ou 'VersionSolution').
    """
    for item in items:
        item_config = item.copy()
        apply_global_config(item_config, global_config)
        item_dir = os.path.join(base_dir, item['NomDossier'])
        
        if 'LienDepotGit' in item:
            Repo.clone_from(item['LienDepotGit'], item_dir)
        #print(item_dir)
        #print(version)
        #print(item_config)
        add_files(item_dir, item_config)
        remove_files(item_dir, item_config, version)
        remove_files(item_dir, global_config, '')
        remove_directories(item_dir, item_config, version)
        remove_directories(item_dir, global_config, '')

def create_zip(zip_name, base_path):
    """
    Crée un fichier ZIP à partir du répertoire spécifié.
    
    :param zip_name: Nom du fichier ZIP à créer.
    :param base_path: Chemin de base du répertoire à zipper.
    """
    shutil.make_archive(zip_name, 'zip', base_path)

def clean_up_directory(directory):
    """
    Supprime le contenu du répertoire spécifié.
    
    :param directory: Répertoire à nettoyer.
    """
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory, exist_ok=True)

def main(config_file):
    """
    Point d'entrée principal du script. Charge la configuration et traite les exemples et exercices.
    
    :param config_file: Chemin vers le fichier de configuration JSON.
    """
    config = load_config(config_file)
    global_config = config.get('ConfigurationGlobal', {})
    
    base_dir = 'output'
    clean_up_directory(base_dir)
    
    sub_dirs = {
        'ExemplesVersionDepart': os.path.join(base_dir, 'Exemples - version de départ'),
        'ExemplesVersionSolution': os.path.join(base_dir, 'Exemples - version solution'),
        'ExercicesVersionDepart': os.path.join(base_dir, 'Exercices - version de départ'),
        'ExercicesVersionSolution': os.path.join(base_dir, 'Exercices - version solution')
    }
    
    for sub_dir in sub_dirs.values():
        os.makedirs(sub_dir, exist_ok=True)
    
    for section in ['Exemples', 'Exercices']:
        for version in ['VersionDepart', 'VersionSolution']:
            version_suffix = 'version de départ' if 'VersionDepart' in version else 'version de solution'
            section_key = f"{section}{version}"
            section_dir = sub_dirs[section_key]
            
            process_items(config.get(section, []), global_config, section_dir, version)
            if version == 'VersionDepart':
                command = ['python', "generate-start-version.py", section_dir, "configuration-start-version.json"]
                result = subprocess.run(command, capture_output=True, text=True)

            add_files_root_zip(section_dir, global_config, section, version)
            zip_name = os.path.join(base_dir, f"{config['NomRencontre']} - {section} - {version_suffix}")
            create_zip(zip_name, section_dir)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python process_files.py <config_filename_for_the_week>")
        sys.exit(1)

    config_filename_for_the_week = sys.argv[1]
    main(config_filename_for_the_week)