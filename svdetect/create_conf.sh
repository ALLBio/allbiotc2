#!/bin/bash
#
# (c) 2013 - Wai Yi Leung
# (c) 2013 AllBio (see AUTHORS file)

# this will modify (a copy of) the template.conf

# DIR is the location of where this bash script is stored
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# PWD is the location of where this bash script was invoked from
PWD=$(pwd)

usage()
{
cat << EOF
usage: $0 options

OPTIONS:
   -h      Show this message
   -o      Outputfile (config)
   -d      Output dir for results
   -e      Tmp dir
   -s      Stats
   -t      threads [1]
   -b      BAM file (mates)
   -r      Reference length
   -v      Verbose
EOF
}

STATSFILE=
OUTPUTFILE=/dev/stdout
BAMFILE=
REFERENCELENGTH=
THREADS=1
OUTPUTDIR=
TMPDIR=
VERBOSE=
while getopts "hd:e:b:r:s:o:t:v" OPTION
do
     case $OPTION in
         h)
             usage
             exit 1
             ;;
         d)
             OUTPUTDIR=$OPTARG
             ;;
         e)
             TMPDIR=$OPTARG
             ;;
         b)
             BAMFILE=$OPTARG
             ;;
         r)
             REFERENCELENGTH=$OPTARG
             ;;
         o)
             OUTPUTFILE=$OPTARG
             ;;
         s)
             STATSFILE=$OPTARG
             ;;
         t)
             THREADS=$OPTARG
             ;;
         v)
             VERBOSE=1
             ;;
         ?)
             usage
             exit
             ;;
     esac
done

if [ -z $STATSFILE ]
then
     echo Missing -S STATSFILE;
     usage
     exit 1
fi

if [ -z $BAMFILE ]
then
     echo Missing -b BAMFILE;
     usage
     exit 1
fi

if [ -z $REFERENCELENGTH ]
then
     echo Missing -R REFERENCELENGTH;
     usage
     exit 1
fi


MU=`cat $STATSFILE  | egrep -v \# | egrep mu | sed -n -r 's/.*mu length \= ([[:digit:]]+),.*/\1/p' /dev/stdin`
SD=`cat $STATSFILE  | egrep -v \# | egrep mu | sed -n -r 's/.*sigma length \= ([[:digit:]]+).*/\1/p' /dev/stdin`

###
## Window size for balanced translocation = 2*mu+2*(2*sigma)^1/2 = 846
## Step = 1/4 of Window size = 211
###

#REDEFINE BAMFILE and REFERENCELENGTH (paths)
BAMFILE="$(echo `readlink -f $BAMFILE` | sed 's:\/:\\\/:g')"
REFERENCELENGTH="$(echo `readlink -f $REFERENCELENGTH` | sed 's:\/:\\\/:g')"
TMPDIR="$(echo `readlink -f $TMPDIR` | sed 's:\/:\\\/:g')"
OUTPUTDIR="$(echo `readlink -f $OUTPUTDIR` | sed 's:\/:\\\/:g')"
WINDOWSIZE=`echo "2*${MU}+2*(2*${SD})^(1/2)" | bc`
WINDOWSTEPSIZE=`echo $WINDOWSIZE/4 | bc`

cat $DIR/template.conf \
 | sed 's/TPL_OUTPUT_DIR/'${OUTPUTDIR}'/' \
 | sed 's/TPL_TMP_DIR/'${TMPDIR}'/' \
 | sed 's/TPL_MATES_FILE/'${BAMFILE}'/' \
 | sed 's/TPL_REFERENCE_LENGTH_FILE/'${REFERENCELENGTH}'/' \
 | sed 's/TPL_THREADS/'${THREADS}'/' \
 | sed 's/TPL_WINDOW_SIZE/'${WINDOWSIZE}'/' \
 | sed 's/TPL_WINDOW_STEP_LENGTH/'${WINDOWSTEPSIZE}'/' \
 | sed 's/TPL_MU_LENGTH/'${MU}'/' \
 | sed 's/TPL_SIGMA_LENGTH/'${SD}'/' > $OUTPUTFILE



