
########################
### Pipeline Setting ###
########################

# SGE configuration.
SGE_PE = BWA

# Keep all intermediate files
.SECONDARY:

# Delete target if recipe returns error status code.
.DELETE_ON_ERROR:

# Makefile specific settings
PWD = $(shell pwd)
THIS_MAKEFILE = $(firstword $(MAKEFILE_LIST))
MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))

#####################
### Used Programs ###
#####################

# Programs folder for custum software. 
PROGRAMS := /virdir/Scratch/software

# BWA. 
BWA = $(BWA_DIR)/bwa

# Dependencies
BWA_DIR := $(PROGRAMS)/bwa-0.7.4
BWA_THREADS = 4
BWA_MAX_INSERT_SIZE := 500 #[500]

#BWA Options
BWA_OPTION_THREADS := 4

BWA_ALN_OPTIONS := -t $(BWA_OPTION_THREADS)
BWA_SAMPE_OPTIONS := -n25 -N25

# Samtools.
SAMTOOLS = $(SAMTOOLS_DIR)/samtools
SAMTOOLS_DIR = /usr/bin

# FastQC 
FASTQC_DIR := $(PROGRAMS)/FastQC
FASTQC := $(FASTQC_DIR)/fastqc
FASTQC_THREADS := 4

# Sickle
SICKLE_DIR := $(PROGRAMS)/sickle-master
SICKLE := $(SICKLE_DIR)/sickle

####################
### Dependencies ###
####################

# References
REFERENCE_DIR := $(MAKEFILE_DIR)/reference
REFERENCE_BWA := $(REFERENCE_DIR)/bwa/reference.fa
REFERENCE := $(REFERENCE_DIR)/reference.fa

##########################
### Input/Output Files ###
##########################

# Files to proces
FASTQ_EXTENSION := fastq
LEFT_SUFFIX := _1
RIGHT_SUFFIX := _2

# input directory, defaults to current directory
IN_DIR := $(shell pwd)

SAMPLE := $(shell ls *$(LEFT_SUFFIX).$(FASTQ_EXTENSION) | python -c 'import os; import sys; print os.path.commonprefix(list(sys.stdin)).split("_")[0]')
PAIRS := $(shell ls *$(LEFT_SUFFIX).$(FASTQ_EXTENSION) | sed 's/$(LEFT_SUFFIX).$(FASTQ_EXTENSION)//')
SINGLES := $(basename $(shell ls *$(LEFT_SUFFIX).$(FASTQ_EXTENSION) *$(RIGHT_SUFFIX).$(FASTQ_EXTENSION)))

# root output directory, defaults to input directory
ROOT_OUT_DIR := $(IN_DIR)

# real output directory
OUT_DIR := $(ROOT_OUT_DIR)

# Set the format of the quality scores in the input files (sanger or solexa).
QSCORE_FORMAT := sanger















# General settings
PEA_MARK := _1
PEB_MARK := _2
FASTQ_EXTENSION := fastq

QSCORE_FORMAT := sanger
THREADS := 8

ALIGNER = bwa-mem


# Samtools.
SAMTOOLS_DIR = /usr/local/samtools/samtools-0.1.18
SAMTOOLS = $(SAMTOOLS_DIR)/samtools




# SGE configuration.
SGE_PE = BWA

# Keep all files (Todo: In view of disk space, maybe we shouldn't do this?).
.SECONDARY:
.ONESHELL:
# Delete target if recipe returns error status code.
.DELETE_ON_ERROR:

# Makefile specific settings
MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))


# Load configuration per pipeline
-include project.conf.mk
