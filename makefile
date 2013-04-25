# preprocess-bwa.mk
#
# Makefile for preprocessing FastQ files -- Part of pipeline for ALLBioTC2
#
# (c) 2013 by Wai Yi Leung [SASC-LUMC]
# 
# Adapted makefile configuration from Wibowo Arindrarto [SASC-LUMC]

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
BWA_DIR := $(PROGRAMS)/bwa-0.7.2
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

###########################
### Input/Outpout Files ###
###########################

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

###############
### Targets ###
###############

# outputdir for all recipies:

SV_PROGRAMS := bd pindel delly

#SV_OUTPUT = $(foreach sample, $(SAMPLE) , $(sample).$(addsuffix .vcf, $(SV_PROGRAMS)))
SV_OUTPUT = $(foreach s, $(SAMPLE), $(foreach p, $(SV_PROGRAMS), $(s).$(p).vcf))
sv_vcf: $(SV_OUTPUT)

# Full pipeline 
all: fastqc alignment aligmentstats sv_vcf

# Partial recipies
FASTQC_FILES = $(addsuffix .raw_fastqc, $(PAIRS)) $(addsuffix .trimmed_fastqc, $(PAIRS))
fastqc: $(addprefix $(OUT_DIR)/, $(FASTQC_FILES))

BAM_FILES = $(addsuffix .sort.bam, $(SAMPLE)) $(addsuffix .sort.bam.bai, $(SAMPLE))
alignment: $(addprefix $(OUT_DIR)/, $(BAM_FILES))

aligmentstats: $(addprefix $(OUT_DIR)/, $(addsuffix .flagstat, $(SAMPLE)) )

.PHONY: test

#########################
### Debug targets     ###
#########################

# Debugging variables
test:
	echo $(CURDIR)
	echo $(MAKEFILE_DIR)
	echo 

#########################
### Rules and Recipes ###
#########################
# creates the output directory
$(OUT_DIR):
	mkdir -p $@

# FastQC for quality control
%.raw_fastqc: %$(LEFT_SUFFIX).$(FASTQ_EXTENSION) %$(RIGHT_SUFFIX).$(FASTQ_EXTENSION)
	mkdir -p $@ && (SGE_RREQ="-now no -pe $(SGE_PE) $(FASTQC_THREADS)" $(FASTQC) --format fastq -q -t $(FASTQC_THREADS) -o $@ $^ || (rm -Rf $@ && false))

%$(LEFT_SUFFIX).trimmed.$(FASTQ_EXTENSION) %$(RIGHT_SUFFIX).trimmed.$(FASTQ_EXTENSION): %$(LEFT_SUFFIX).$(FASTQ_EXTENSION) %$(RIGHT_SUFFIX).$(FASTQ_EXTENSION)
	$(SICKLE) pe -f $(word 1, $^) -r $(word 2, $^) -t sanger -o $(basename $(word 1, $^)).trimmed.fastq -p $(basename $(word 2, $^)).trimmed.fastq -s $(basename $(word 1, $^)).singles.fastq -q 30 -l 25 > $(basename $(word 1, $^)).filtersync.stats

# FastQC to check trimming
%.trimmed_fastqc: %$(LEFT_SUFFIX).trimmed.$(FASTQ_EXTENSION) %$(RIGHT_SUFFIX).trimmed.$(FASTQ_EXTENSION)
	mkdir -p $@ && (SGE_RREQ="-now no -pe $(SGE_PE) $(FASTQC_THREADS)" $(FASTQC) --format fastq -q -t $(FASTQC_THREADS) -o $@ $^ || (rm -Rf $@ && false))

# BWA Alignment create .sai files from fastq files
%.sai: %.trimmed.$(FASTQ_EXTENSION)
	SGE_RREQ="-pe $(SGE_PE) $(BWA_OPTION_THREADS)" $(BWA) aln $(BWA_ALN_OPTIONS) $(if $(findstring sanger, $(QSCORE_FORMAT)),,-I) $(REFERENCE_BWA) $< > $@

# BWA Alignment, create a samfile from two sai files from a paired end sample
%.sam: %$(LEFT_SUFFIX).sai %$(RIGHT_SUFFIX).sai %$(LEFT_SUFFIX).trimmed.$(FASTQ_EXTENSION) %$(RIGHT_SUFFIX).trimmed.$(FASTQ_EXTENSION)
	$(BWA) sampe $(BWA_SAMPE_OPTIONS) $(REFERENCE_BWA) $^ > $@

# SamTools view, convert sam to bam format
%.bam: %.sam
	$(SAMTOOLS) view -bST $(REFERENCE) -o $@ $<

# Samtools sort, sort the bamfile.
%.sort.bam: %.bam
	$(SAMTOOLS) sort $< $(basename $@)

# Samtools Flagstat
%.flagstat: %.sort.bam
	$(SAMTOOLS) flagstat $< > $@

# Samtools index
%.sort.bam.bai: %.sort.bam
	$(SAMTOOLS) index $<




#####
## Call the SV files
#####

%.bd.vcf: %.sort.bam
	$(MAKE) -C $(PWD) -f $(MAKEFILE_DIR)/breakdancer/Makefile $@

%.pindel.vcf: %.sort.bam
	$(MAKE) -C $(PWD) -f $(MAKEFILE_DIR)/pindel/Makefile REFERENCE=$(REFERENCE) IN=$< OUT=$@

%.delly.vcf: %.sort.bam
	$(MAKE) -C $(PWD) -f $(MAKEFILE_DIR)/delly/Makefile REFERENCE=$(REFERENCE) $@











