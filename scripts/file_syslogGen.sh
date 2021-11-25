#!/bin/bash
# -----------------------------------------------------------------------
# To simulate rsyslog data into various facilities and locations
# This takes user input of PORT and fileinput from templates 
# -----------------------------------------------------------------------

PORT_IN=$1

# Optional: Format has to be either sd or msg. (Defaults to msg)
FORMAT=$2

if [[ $PORT_IN || $PORT_IN = *[^0-9]* ]]
then
    echo "INFO: Will try to Send message to PORT $PORT_IN" 
else
    echo "ERROR: No Input specified. Expected Input is PORT NUMBER"
    echo "Usage: $0 <port_number>"
    exit 1
fi


if [[ $FORMAT = "sd" ]]
then
    echo "INFO: Message format is Structured-Data (SD)"
    FORMAT="sd"
else
    echo "INFO: Message format is non-Structured (msg)"
    FORMAT="msg"
fi

# Path to netcat
NC="/usr/bin/nc"
ORIG_IPS_FILE="../artefacts/rsyslog_functional_configs/hostnames.sample"
SYS_TEMPLATE_DIR="../artefacts/rsyslog_functional_data"
DEST_IP="127.0.0.2"

which $NC 1>&2>/dev/null
if [[ $? -ne 0 ]]
then
    echo "ERROR: $NC NOT present. Quitting.."
    exit 1
fi

# Netcat parameters
COUNT=1
DELAY=1

# The filename should have <facility>.<priority> format in its name
# eg:  local6.182.info.log.template
for inFile in `ls $SYS_TEMPLATE_DIR/*log.template`
do
  facility=`basename $inFile | awk -F'.' '{print $1}'`
  priority=`basename $inFile | awk -F'.' '{print $2}'`
  echo "INFO: Sending InputFile=$inFile facility=$facility priority=$priority "
    cat $inFile | while read RANDOM_MESSAGE 
    do
        for ORIG_IP in `cat $ORIG_IPS_FILE`
        do
		    if [ $FORMAT = "sd" ]
		    then 
		       payload="<$priority>1 `date "+%FT%T"`.000Z ${ORIG_IP} my-sd-app 12345 my-sd-msgid [${RANDOM_MESSAGE}]"
		    else
		       payload="<$priority>`env LANG=us_US.UTF-8 date "+%b %d %H:%M:%S"` ${ORIG_IP} $RANDOM_MESSAGE"
            fi			   
		  
            # echo "DEBUG: Sending to DEST_IP=$DEST_IP PORT=$PORT_IN DELAY=$DELAY payload=$payload"
            $NC $DEST_IP -u $PORT_IN -w $DELAY <<< $payload	
        done
    done
done

# https://github.com/Graylog2/graylog-guide-syslog-linux
# RFC5424 Standard message should be in below format. This is NOT a template, but the format STRUCTURE of the SD message
# "<%PRI%>%PROTOCOL-VERSION% %TIMESTAMP:::date-rfc3339% %HOSTNAME% %APP-NAME% %PROCID% %MSGID% %STRUCTURED-DATA% %msg%\n"

