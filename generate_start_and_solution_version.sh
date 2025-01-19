#!/bin/bash

# Term to search for in directory names
SEARCH_TERM="r01-r02"

# Target directory to copy matching directories to
TARGET_DIR_START_VERSION="generated_start_version_tmp_output"
TARGET_DIR_SOLUTION_VERSION="generated_solution_version_tmp_output"

# Source directory containing the folders to search
SOURCE_DIR=".."

# Create the targets directories if they doesn't exist
mkdir -p "$TARGET_DIR_START_VERSION"
mkdir -p "$TARGET_DIR_SOLUTION_VERSION"

# Clear the target directory
rm -rf "$TARGET_DIR_START_VERSION/*"
rm -rf "$TARGET_DIR_SOLUTION_VERSION/*"

# Find and copy directories matching the search term from the source directory
find "$SOURCE_DIR" -type d -name "*$SEARCH_TERM*" | while read dir; do
  if [ "$(realpath "$dir")" != "$(realpath "$TARGET_DIR_START_VERSION")/$(basename "$dir")" ]; then
    rsync -av --exclude='.git' "$dir/" "$TARGET_DIR_START_VERSION/$(basename "$dir")"
  fi
  if [ "$(realpath "$dir")" != "$(realpath "$TARGET_DIR_SOLUTION_VERSION")/$(basename "$dir")" ]; then
    rsync -av --exclude='.git' "$dir/" "$TARGET_DIR_SOLUTION_VERSION/$(basename "$dir")"
  fi
done
echo "Directories containing '$SEARCH_TERM' from '$SOURCE_DIR' have been copied to '$TARGET_DIR_START_VERSION' and '$TARGET_DIR_SOLUTION_VERSION'."

# Unleash the disney magic
#python generate-start-version.py $TARGET_DIR_START_VERSION -v versiondepart
#python generate-start-version.py $TARGET_DIR_SOLUTION_VERSION -v versionsolution