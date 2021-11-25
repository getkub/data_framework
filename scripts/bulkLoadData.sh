#!/bin/bash
# ======================================================
# Script to load Data in bulk based on rules
# This will load Data from entire $sample_dataDir folder
# The rules are written in strict GUIDELINES. 
# Please DO NOT change without understanding them
v=0.1
# This script will pass handle over to eventgen to create file 
# ======================================================

mapping="../configs/index_st_map.csv"
eventgenApp="/tmp/eventgen"
sample_dataDir="../artefacts/evg_sample_functional_data"
outputDir="/tmp/simulatedData"
fileID=`date +%Y%m%d%H%M`

mkdir -p $outputDir
rm -rf $outputDir/*

# config file specific variables
tokenTemplate="../configs/eventgen_tokens.template"
configTemplate="../configs/eventgen_configs.template"

# -------------------------------------------------------------
# Loop through the Mapping File. Get all files
# Create sample config file and dataset and pass it to eventgen
# -------------------------------------------------------------

for line in `cat $mapping`
do
  index=`echo $line| awk -F',' '{print $1}'`
  st=`echo $line| awk -F',' '{print $2}'`
  st_file=`echo $line| awk -F',' '{print $3}'`
  if [ -f ${sample_dataDir}/${st_file} ]
  then
      #echo index=$index st=$st st_file=$st_file 
      echo "Creating Template for $st"
      outputFile="${outputDir}/${st_file}.${fileID}.auto.conf" 
      echo "[${st_file}]" > $outputFile
      echo "outputMode = file" >> $outputFile
      echo "fileName = ${outputDir}/${st_file}.${fileID}.output" >> $outputFile
      echo ""  >> $outputFile
      cat $configTemplate >> $outputFile
      echo ""  >> $outputFile
      cat $tokenTemplate >> $outputFile 

  fi
done

# Now the funny bit. Take all the conf files generated and copy to eventgen "local"
# Copy the sample datasets to "samples" directory  and then run the eventgen in Threaded mode

#In case Eventgen NOT present in /tmp
rsync -avhi --size-only --quiet ../eventgen ${eventgenApp}/.. 

echo "copying conf files and samples to eventgen"
rm ${eventgenApp}/local/*auto.conf
mv ${outputDir}/*${fileID}.auto.conf ${eventgenApp}/local/
rsync -avhi --size-only --quiet $sample_dataDir/* ${eventgenApp}/samples/

echo "Now triggering eventgen"
for gen in `ls ${eventgenApp}/local/*${fileID}.auto.conf`
do
   # echo "Triggering: $gen to eventgen"
  /opt/splunk/bin/splunk cmd python ${eventgenApp}/bin/eventgen.py $gen & 
done

echo ""
echo "Please Wait .... " 
sleep 10 
echo "Please Wait .... "
sleep 20 
echo "This will take some time anyway, so be patient"
sleep 30 
echo "Please Wait ...."
sleep 60

echo "Now indexing the files to SPLUNK >>"

for inFile in `ls ${outputDir} | grep ${fileID}.output`
do
   stLine=`echo $inFile | awk -F'.' '{print $1}'` 
   myst=`grep -w $stLine ${mapping} | tail -1| awk -F',' '{print $2}'`
   myindex=`grep -w $stLine ${mapping} | tail -1| awk -F',' '{print $1}'`
   /opt/splunk/bin/splunk add oneshot -source ${outputDir}/${inFile} -index $myindex -sourcetype $myst
done

# After waiting for for some-more time, Find and kill any eventgen process
ps -ef | grep eventgen| grep -v grep | awk -F' ' '{print $2}' | xargs kill -9 



