# conf.mk - Pipeline configuration for AllBioTC2
#
# (c) 2013 - Wai Yi Leung
# (c) 2013 AllBio (see AUTHORS file)
# 
# Adapted makefile configuration from Wibowo Arindrarto [SASC-LUMC]

########################
### Pipeline Setting ###
########################

# SGE configuration.
SGE_PE = BWA

# Keep all intermediate files
#.SECONDARY:

# Delete target if recipe returns error status code.
.DELETE_ON_ERROR:

# Makefile specific settings
PWD = $(shell pwd)
THIS_MAKEFILE = $(firstword $(MAKEFILE_LIST))
MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))

#(test) data generation configuration

GENERATE_DATA := TRUE
DATA_PREFIX := sim-reads
INSERT_SIZE := 500
SD := 50
READLENGTH := 100
COVERAGE := 30
DUPLICATE := 0.01
TOTALREADLENGTH= $(shell expr 2 \* $(READLENGTH))
GENOMELENGTH := 119667750
READCOUNT= $(shell expr $(COVERAGE) \* $(GENOMELENGTH) / $(TOTALREADLENGTH))
DATASET=$(INSERT_SIZE)_$(SD)
GENOME_FILE := genome.fasta	

#####################
### Used Programs ###
#####################

# Programs folder for custom software. 
PROGRAMS := /opt/allbio/software/
PROGRAMS_DIR := $(PROGRAMS)

# laser
LASER := $(PROGRAMS)/laser/clever-toolkit-v2.0rc2/bin/laser

# BWA. 
BWA_VERSION=bwa-v0.7.5a
BWA = $(BWA_DIR)/bwa

# BOWTIE2. 
BOWTIE2_DIR := $(PROGRAMS)/bowtie2-2.1.0
BOWTIE2 := $(BOWTIE2_DIR)/bowtie2

# Dependencies
BWA_DIR := $(PROGRAMS)/bwa/$(BWA_VERSION)
BWA_THREADS := 4
BWA_MAX_INSERT_SIZE := 500 #[500]

#BWA Options
BWA_OPTION_THREADS := 4

BWA_ALN_OPTIONS := -t $(BWA_OPTION_THREADS)
BWA_SAMPE_OPTIONS := -n25 -N25

# FastQC 
FASTQC_VERSION := fastqc_v0.10.1
FASTQC_DIR := $(PROGRAMS)/FastQC/$(FASTQC_VERSION)
FASTQC := $(FASTQC_DIR)/fastqc
FASTQC_THREADS := 4

# Sickle
SICKLE_VERSION := sickle-v1.2.1
SICKLE_DIR := $(PROGRAMS)/sickle/$(SICKLE_VERSION)
SICKLE := $(SICKLE_DIR)/sickle

# Samtools.
SAMTOOLS_VERSION := samtools-v0.1.19
SAMTOOLS_DIR := $(PROGRAMS)/samtools/$(SAMTOOLS_VERSION)
SAMTOOLS := $(SAMTOOLS_DIR)/samtools

# Python, can be changed to a version which is not installed with the system
# for example, a version which is installed in a virtualenv with the required
# libraries. For information about venv's: http://www.virtualenv.org/

PYTHON_EXE := python

####################
### Dependencies ###
####################

# References
REFERENCE_DIR := $(MAKEFILE_DIR)/reference
REFERENCE_BWA := $(REFERENCE_DIR)/bwa/reference.fa
REFERENCE_BOWTIE2 := $(REFERENCE_DIR)/bowtie2/reference
REFERENCE := $(REFERENCE_DIR)/reference.fa

# meerkat reference files
DATA_REPEAT_MASKER := $(REFERENCE_DIR)/db/hg19/repeatMask
DATA_REFERENCE := $(REFERENCE_DIR)/#db/hg19_fasta
DATA_THREADS := 8
DATA_BWA_INDEXED_REF:= $(REFERENCE_DIR)/bwa/reference.fa
DATA_FASTA_INDEX := $(REFERENCE_DIR)/reference.fa.fai
DATA_HEADERFILE := $(REFERENCE_DIR)/db/headerfile


##########################
### Input/Output Files ###
##########################

# General settings
PEA_MARK := .1
PEB_MARK := .2
FASTQ_EXTENSION := fastq

# Set the format of the quality scores in the input files (sanger or solexa).
QSCORE_FORMAT := sanger
THREADS := 8

ALIGNER := bwa-mem

# input directory, defaults to current directory
IN_DIR := $(shell pwd)
#if data needs to be generated first there are no samples in the input directory!!
ifneq ($(GENERATE_DATA) , TRUE)
SAMPLE := $(shell ls *$(PEA_MARK).$(FASTQ_EXTENSION) | python -c 'import os; import sys; print os.path.commonprefix(list(sys.stdin)).split(".")[0]')
PAIRS := $(shell ls *$(PEA_MARK).$(FASTQ_EXTENSION) | sed 's/$(PEA_MARK).$(FASTQ_EXTENSION)//')
SINGLES := $(basename $(shell ls *$(PEA_MARK).$(FASTQ_EXTENSION) *$(PEB_MARK).$(FASTQ_EXTENSION)))
endif

#Compose filenames from configuration parameters
ifeq ($(GENERATE_DATA) , TRUE)
SAMPLE := $(DATA_PREFIX)_$(DATASET)
PAIRS := $(DATA_PREFIX)_$(DATASET)
SINGLES := $(DATA_PREFIX)_$(DATASET)$(PEA_MARK)$(DATA_PREFIX)_$(DATASET)$(PEB_MARK)
endif
# root output directory, defaults to input directory
ROOT_OUT_DIR := $(IN_DIR)

# real output directory
OUT_DIR := $(ROOT_OUT_DIR)

# reference VCF used in this project
REFERENCE_VCF :=

# tool versions
CLEVER_VERSION := -sv



# Load configuration per pipeline
-include project.conf.mk
