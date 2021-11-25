#!/bin/bash
# ======================================================
# Script to generate Data by cloning template exactly ONE time
# The rules are written in strict GUIDELINES. 
# Please DO NOT change without understanding them
v=0.1
# This script will pass handle over to eventgen to create file 
# ======================================================

IN_DATA=$1
DEBUG=$2

if [[ ! $IN_DATA || ! -f $IN_DATA ]]
then
    echo "ERROR: No Input specified or file NOT present. Expected Input is CSV file"
    echo "Usage for Replay: $0 <sanitised_file_in_csv>"
    exit 1
fi

# Check if the File Headers are good and contain index, _raw, sourcetype etc.
echo "INFO: Validating inputdata"
head -1 $IN_DATA| grep index | grep _raw |  grep -q sourcetype
if [ "$?" != "0" ]
then
    echo "ERROR: Input File is NOT in expected format. Needs to contain Headers in required CSV format"
    exit 200
fi

if [ "$DEBUG" == "debug" ]
then
   echo "DEBUG is ON"
   DEBUGFLAG="-v"
else
   DEBUGFLAG=""
fi

#Waiting time in seconds
eventgenApp="/tmp/eventgen"
mkdir -p $eventgenApp
fileID=`date +%Y%m%d%H%M`

echo "INFO: Getting Config files"
# config file specific variables
tokenTemplate="../configs/eventgen_tokens.template"
# Below is the MOST important file. The settings are chosen very carefully
configTemplate="../configs/eventgen_clone_configs.template"

# Create the .conf file for eventgen
st_file=`basename $IN_DATA`
rm /tmp/${st_file}*.auto.conf 2>/dev/null
outputFile="/tmp/${st_file}.${fileID}.auto.conf"
echo "[${st_file}]" > $outputFile
cat $configTemplate   >> $outputFile
cat $tokenTemplate  >> $outputFile

# ---------------------------------------------------------------------------------------
# Now the funny bit. Take all the conf files generated and copy to eventgen "local"
# Copy the sample datasets to "samples" directory  and then run the eventgen in single mode
# ---------------------------------------------------------------------------------------

#In case Eventgen NOT present in /tmp
echo "INFO: Syncing configs"
rsync -avhi --size-only --quiet ../eventgen ${eventgenApp}/.. 
rm ${eventgenApp}/local/*auto.conf 2>/dev/null
mv ${outputFile} ${eventgenApp}/local/
rsync -avhi --size-only --quiet $IN_DATA ${eventgenApp}/samples/


echo "INFO: Triggering eventgen and Indexing"
for gen in `ls ${eventgenApp}/local/*${fileID}.auto.conf`
do
   echo "Triggering: $gen to eventgen"
   /opt/splunk/bin/splunk cmd python ${eventgenApp}/bin/eventgen.py $DEBUGFLAG $gen & 
done


## Assuming all should stop within 10 seconds, quitting
sleep 20
echo "INFO: Finished eventgen and Indexing"

exit 0

