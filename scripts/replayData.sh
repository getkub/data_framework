#!/bin/bash
# ======================================================
# Script to generate Data for specific functional testing 
# The rules are written in strict GUIDELINES. 
# Please DO NOT change without understanding them
v=0.1
# This script will pass handle over to eventgen to create file 
# ======================================================

IN_DATA=$1
FORMAT=$2
DEBUG=$3

if [[ ! $IN_DATA || ! -f $IN_DATA ]]
then
    echo "ERROR: No Input specified or file NOT present. Expected Input is Replay CSV file"
    echo "Usage for Replay: $0 <sanitised_file_in_csv> <replay/sample>"
    exit 1
fi

if [ "$FORMAT" == "sample" ]
then
   configModeTemplate="../configs/eventgen_sample_configs.template"
   wait_time=30
   wait_block=1
elif [ "$FORMAT" == "replay" ]
then
   configModeTemplate="../configs/eventgen_replay_configs.template"
   wait_time=120
   wait_block=4
else
    echo "ERROR: The second parameter should be either sample or replay "
    echo "Usage for Replay: $0 <sanitised_file_in_csv> <replay/sample>"
    exit 1
fi

# Check if the File Headers are good and contain index, _raw, sourcetype etc.
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
sample_dataDir="../artefacts/evg_replay_functional_data/"
fileID=`date +%Y%m%d%H%M`

# config file specific variables
tokenTemplate="../configs/eventgen_tokens.template"
configTemplate="../configs/eventgen_configs.template"



# Create the .conf file for eventgen
st_file=`basename $IN_DATA`
rm /tmp/${st_file}*.auto.conf 2>/dev/null
outputFile="/tmp/${st_file}.${fileID}.auto.conf"
echo "[${st_file}]" > $outputFile
cat $configModeTemplate   >> $outputFile
cat $tokenTemplate  >> $outputFile

# ---------------------------------------------------------------------------------------
# Now the funny bit. Take all the conf files generated and copy to eventgen "local"
# Copy the sample datasets to "samples" directory  and then run the eventgen in single mode
# ---------------------------------------------------------------------------------------

#In case Eventgen NOT present in /tmp
rsync -avhi --size-only --quiet ../eventgen ${eventgenApp}/.. 
rm ${eventgenApp}/local/*auto.conf 2>/dev/null
mv ${outputFile} ${eventgenApp}/local/
rsync -avhi --size-only --quiet $sample_dataDir/* ${eventgenApp}/samples/
# Sometimes the sample is present only in provided input file
rsync -avhi --size-only --quiet $IN_DATA ${eventgenApp}/samples/


echo "INFO: Triggering eventgen and Indexing"
for gen in `ls ${eventgenApp}/local/*${fileID}.auto.conf`
do
   echo "Triggering: $gen to eventgen"
   /opt/splunk/bin/splunk cmd python ${eventgenApp}/bin/eventgen.py $DEBUGFLAG $gen & 
done

wait_time_block=`expr $wait_time / $wait_block`
for((i=0;i<$wait_block;++i)) do
    remaingTime=`echo "$wait_time - $i * $wait_time_block" | bc`
    echo "Please Wait ....($remaingTime)s"
    sleep $wait_time_block
done

# After waiting for for some-more time, Find and kill any eventgen process
ps -ef | grep eventgen| grep -v grep | awk -F' ' '{print $2}' | xargs kill -9 



