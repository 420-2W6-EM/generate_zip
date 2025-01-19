# Générateur de version de départ et de version de solution et générateur de ZIPs


# Préalable
- La fonctionnalité WSL (Ubuntu) doit être activié sous Windows et le script doit être lancé à partir de WSL
- Dans WSL, dos2unix doit être installé, python ainsi que gitpython (pip install gitpython)
- Tous les dépôts d'exemples et d'exercices doivent être présent dans le répertoire précédent ".."


# Script - generate-start-and-solution-version.py

Permet de transformer le contenu d'un répertoire en une version soit de départ ou de solution. Les fichiers sont remplacés. Il faut donc exécuter ce script python sur une copie du répertoire avec les fichiers.

`code`
python generate-start-and-solution-version.py -v versiondepart $TARGET_DIR_START_VERSION 
python generate-start-and-solution-version.py -v versionsolution $TARGET_DIR_SOLUTION_VERSION
`code`

Par défault, le script utilise le fichier de configuration configuration-start-version.json afin de savoir quelles extensions de fichier prendre en compte et la liste des balises devant être utilisés. Il est possible d'en spécifié un autre avec le flag -c, mais ça ne devrait pas être utiliser à moins pour des tests.


# Script - generate-start-and-solution-version.sh

Ce script sert à recopier un exemple de répertoires, par exemples des exemples et des exercices pour une semaine, vers deux répertoires. Un répertoire qui contiendra la version de départ du code, et une version contenant la version solution du code.

Les répertoires sont :
- "generated-start-version-tmp-output" (version de départ)
- "generated-solution-version-tmp-output" (version solution)

Il est possible de modifier dans le script la ligne #4 afin d'indiquer un terme qui doit être présent dans les dossiers de code à répliquer. Par exemple, si le terme "r01-r02" est présent, tous les répertoires de code présent dans le répertoire ".." portant ce terme seront recopier dans les 2 répertoires "tmp-out".

Par la suite, le script va lancé l'appel python à generate-start-and-solution-version.py afin de généré la version de solution et la version de départ. Ce script devrait être utilisé sur les postes des enseignants uniquements pour des fins de tests afin d'observer rapidement le résultat de la transformation en observant le contenu des 2 répertoires. Ces répertoires sont dans le .gitignore et ne devraient pas être commité.

# Script - generate-zips-for-week.py

Ce script va générer 4 fichiers ZIP (exemple départ, exemple solution, exercice départ, exercice solution) en se basant sur la configuration d'un fichier JSON. Pour un exemple de fichier, voir le fichier "configuration-week1-r01-r02.json". Le fichier permet de définir le nom des répertoires, les liens vers les dépôts GIT (un git clone est fait par le script), des listes fichiers supplémentaires à rajoutés dans certaines versions de zip (ex : instructions.docx).

Le répertoire "generated-zips-tmp-out" permet de voir le résultat de l'outil (ainsi que les 4 zips généré). L'outil fait appel à l'outil "python generate-start-and-solution-version.py" pour généré les versions de départ ou de solution en conséquence. Ce qui est observable dans le répertoire "generated-zips-tmp-out" est exactement ce qui sera dans les ZIPs. Le répertoire "generated-zips-tmp-out" est également dans le .gitignore et ne devrait pas être comité.

Les ZIPs sont copiés vers le répertoire "zip-generated". Il y a des pipelines dans le dépôt "generate-zip" qui permet de lancer l'exécution de l'outil. Les ZIP généré sont commité dans le répertoire zip-generated. Il est ainsi possible d'y faire référence. Éventuellement, il serait possible de faire en sorte qu'un commit sur l'importe quelle exemple et exercice mets à jour la version disponible en ligne, mais également lancerait la génération du ZIP pour le mettre à jour.

Pour l'instant, tous les fichiers "statics" à inclure dans les ZIP sont dans le répertoire "files-to-include-in-zip" du git en attendant de trouver une solution de connectivité vers OneDrive ou Teams (complexe pour le moment).