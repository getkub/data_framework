#!/bin/bash
# -----------------------------------------------------------------------
# DO NOT MODIFY this script, but take a copy and edit it
# -----------------------------------------------------------------------
# Path to netcat
NC="/usr/bin/nc"
# Where are we sending messages from / to?
#ORIG_IPS=("172.31.68.202" "172.31.154.4" "172.31.68.3" "127.0.0.1" )
ORIG_IPS=("172.31.68.202" "someRandom.host.com")
#DEST_IPS=("127.0.0.2" "123.456.28.9" "172.111.222.333")
DEST_IPS=("127.0.0.2" "localhost")
# List of messages.
MESSAGES=("Error Event" "Warning Event" "Info Event")
#PORTS=("514" "10514" "10515" "10516" "10517")
PORTS=("514")
SYSLOGTAGS=("hostd" "crond" "vmkernel" "snmpd")
# How long to wait in between sending messages.
SLEEP_SECS=1
# How many message to send at a time.
COUNT=1
# What priority?
#             emergency   alert   critical   error   warning   notice   info   debug
# kernel              0       1          2       3         4        5      6       7
# user                8       9         10      11        12       13     14      15
# mail               16      17         18      19        20       21     22      23
# system             24      25         26      27        28       29     30      31
# security           32      33         34      35        36       37     38      39
# syslog             40      41         42      43        44       45     46      47
# lpd                48      49         50      51        52       53     54      55
# nntp               56      57         58      59        60       61     62      63
# uucp               64      65         66      67        68       69     70      71
# time               72      73         74      75        76       77     78      79
# security           80      81         82      83        84       85     86      87
# ftpd               88      89         90      91        92       93     94      95
# ntpd               96      97         98      99       100      101    102     103
# logaudit          104     105        106     107       108      109    110     111
# logalert          112     113        114     115       116      117    118     119
# clock             120     121        122     123       124      125    126     127
# local0            128     129        130     131       132      133    134     135
# local1            136     137        138     139       140      141    142     143
# local2            144     145        146     147       148      149    150     151
# local3            152     153        154     155       156      157    158     159
# local4            160     161        162     163       164      165    166     167
# local5            168     169        170     171       172      173    174     175
# local6            176     177        178     179       180      181    182     183
# local7            184     185        186     187       188      189    190     191

# Put list of Priorities within brackets
PRIORITIES=(128 129 130 131 132 133 134 135 142 150 158 166 174 182)
#PRIORITIES=(3 6 11 14 19 22 83 86)
while [ 1 ]
do
        for i in $(seq 1 $COUNT)
        do
                # Picks a random syslog message from the list.
                RANDOM_MESSAGE=${MESSAGES[$RANDOM % ${#MESSAGES[@]} ]}
                PRIORITY=${PRIORITIES[$RANDOM % ${#PRIORITIES[@]} ]}
                PORT=${PORTS[$RANDOM % ${#PORTS[@]} ]}
                ORIG_IP=${ORIG_IPS[$RANDOM % ${#ORIG_IPS[@]} ]}
                DEST_IP=${DEST_IPS[$RANDOM % ${#DEST_IPS[@]} ]}
                SYSLOGTAG=${SYSLOGTAGS[$RANDOM % ${#SYSLOGTAGS[@]} ]}
                echo "Sending Message : PRIORITY=$PRIORITY ORIG_IP=$ORIG_IP SYSLOGTAG=$SYSLOGTAG RANDOM_MESSAGE=$RANDOM_MESSAGE"
                $NC $DEST_IP -u $PORT -w 1 <<< "<$PRIORITY>`env LANG=us_US.UTF-8 date "+%b %d %H:%M:%S"` $ORIG_IP $SYSLOGTAG: $RANDOM_MESSAGE"
        done
        sleep $SLEEP_SECS
done

