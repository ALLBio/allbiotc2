#!/bin/bash

# Environment logger, part of SASC rig framework (C) 2013 LUMC-SASC
#
# (c) 2013 - Wai Yi Leung
# (c) 2013 - LUMC-SASC (http://www.lumc.nl/)


# make sure we have a logfolder
mkdir -p .log

# the command to be executed
run_cmd=$@

# we can skip the timing for the shell commands containing pipes
if [[ "$run_cmd" == *"|"* ]];
then
    skipTime=1
else
    skipTime=0
fi


# check whether this is invoked using the $(shell command) from Make
case $@ in
    "-c "*)
        run_cmd=${run_cmd#"-c "}
    ;;
esac

# calculate the md5sum from the command
md5sum=$(echo -n "$run_cmd" | md5sum | cut -f 1 -d' ')
base=$(basename "$THIS_MAKEFILE")
jobrunid="${base%.*}.`date +%s`.$RANDOM"

# strip the SGE_REQ variables
SGE='SGE_RREQ="*" '
run_cmd=${run_cmd##$SGE}
# write the command to the master.log
echo "$jobrunid: $run_cmd" >> .log/master.log

if [[ $skipTime == 1 ]];
then
    eval "$run_cmd"
    exitcode=$?
else
    run_cmd=$(echo $run_cmd | sed -e 's/\"/\\"/g' )
    { { /usr/bin/time -v -o .log/$jobrunid.stat.log -- sh -c "$run_cmd" | tee .log/$jobrunid.stdout.log >&3; exit ${PIPESTATUS[0]}; } 2>&1 | tee .log/$jobrunid.stderr.log >&2; } 3>&1
    # exitcode is on the last line of the .log/stat.log
    exitcode=`cat .log/$jobrunid.stat.log | egrep "Exit status"| tr -d ' ' | cut -d':' -f2`
fi

exit $exitcode
