#!/bin/bash
############################################################
# Help                                                     #
############################################################
help()
{
   # Display Help
   echo
   echo "Syntax: launch.sh <-b number> <-e number> <-s number> <-p string> <-i inventory>"
   echo "options:"
   echo "-b number	beginning of wrk rate"
   echo "-e number	end of wrk rate."
   echo "-s number	auto increment wrk rate step"
   echo "-p string	prefix to result output dir."
   echo "-i inventory	inventory file."
   echo
}


START=""
STOP=""
STEP=""
PREFIX=""
INVENTORY="inventory"

check()
{
    if [ "z$START" == "z" ] || [ "z$STOP" == "z" ] || [ "z$STEP" == "z" ] || [ "z$PREFIX" == "z" ] || [ ! -f $INVENTORY ];
    then
      help
      exit -1
    fi
}

while getopts ":hb:e:s:p:i:" option; do
  case $option in
    h) # help
      help
      exit;;
    b) # start
      START=$(($OPTARG + 0));;
    e)
      STOP=$(($OPTARG + 0));;
    s)
      STEP=$(($OPTARG + 0));;
    p)
      PREFIX=$OPTARG;;
    i)
      INVENTORY=$OPTARG;;
    \?) # invalid option
      help
      exit -1;;
  esac
done

check

rate=$START

while [ $rate -le $STOP ];
do
  result="${PREFIX}_${rate}"
  echo "Start trying with rate $rate $result..."
  sleep 5
  ansible-playbook -i $INVENTORY run_wrk_emon.yaml -e need_emon=true -e redeploy=true -e result_dir="${result}" -e wrk_rate=${rate}
  rate=$(($rate + $STEP))
done


