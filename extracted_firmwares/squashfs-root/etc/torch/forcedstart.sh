#!/bin/sh

DSTIP="8.8.8.8"
REPCNT=30
LOGFILE="/tmp/torchapi.log"
TIMESTAMP="date +%s"
SLEEPTIME=3

[ ! -z "$1" ] && {
    REPCNT=$1
}

cnt=$((REPCNT / (SLEEPTIME + 1) ))
while true; do

  echo [`$TIMESTAMP`"] Wait, checking internet connection [$cnt]" >> $LOGFILE

  ret=$(/bin/ping -w1 -c2 "$DSTIP" 2>/dev/null)
  
  if [ ! -z "$ret" ]; then  
    ret=$(echo "$ret" | grep 'rec' | awk -F'[ ]' '{print $4}')
    	
    [ ! -z "$ret" ] && [ "$ret" -gt 0 ] && break
  fi

  if [ "$cnt" -ge 1 ]; then
    cnt=$(($cnt - 1))
  else
    break
  fi
  
  sleep "$SLEEPTIME"
done

/etc/torch/update_firmware

# repeat request for added devices
/etc/torch/device_add_unmonit

/etc/torch/check_config

