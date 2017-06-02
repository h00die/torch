#!/bin/sh

pid=$(pidof squid | awk -F" " '{print $1}')

if [ ! -z $pid ]; then
 psmsg=$(/usr/bin/ps -p $pid -o %cpu,%mem,cmd)
 cpu=$(echo $psmsg | awk -F" " '{print $4}')
 mem=$(echo $psmsg | awk -F" " '{print $5}')
 cmd=$(echo $psmsg | awk -F" " '{print $6}')
 	
 echo $cpu $mem $cmd

 echo "[`date +%s`]> Check Squid resourse usage. CPU=$cpu/MEM=$mem/CMD=$cmd/PID=$pid" >> /tmp/torchapi.log

 cpu_alm=$(echo $cpu '>'90 | bc -l)
 mem_alm=$(echo $mem '>'90 | bc -l)

 if [ "$cpu_alm" -ge 1 ] || [ "$mem_alm" -ge 1 ]; then
   echo "[`date +%s`]> ALARM. Restart Squid!" >> /tmp/torchapi.log
   /etc/init.d/squid restart
 fi
fi

exit 0
