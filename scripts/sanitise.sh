#!/bin/bash
# ======================================================
# Script to sanitise Data based on pattern provided 
# Ensure you take backup of your file before, as this script will do in-line replace
# ======================================================

# Ruleset based on PERL regex
ruleset="../configs/ruleset_sanitise.pel"

if [ "$#" -ne 1 ] || ! [ -f "$1" ]; then
  echo "ERROR: File NOT found or NO input given"
  echo "Usage: $0 file_to_sanitise_absolute_path" >&2
  exit 1
fi
fileToModify=$1

echo "File to Sanitise => $fileToModify "

# ======================================================
# NOTE: This will modify file INLINE
# This means your ORIGINAL FILE will be modified
# ======================================================
for rule in `cat $ruleset | egrep -v "^#"`
do
  echo "Applying Rule: ${rule} ..."  
  eval perl -p -i -e '${rule}' $fileToModify 
done

# Remove any backup files created
echo "Removing any backup files"
rm ${fileToModify}.bak
