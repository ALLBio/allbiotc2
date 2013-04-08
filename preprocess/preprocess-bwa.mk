########################
### Preprocess       ###
########################

########################
### Pipeline Setting ###
########################

SQ_CENTER = BGI
PLATFORM = ILLUMINA

# SGE configuration.
SGE_PE = BWA

# Keep all files (Todo: In view of disk space, maybe we shouldn't do this?).
.SECONDARY:

# Delete target if recipe returns error status code.
.DELETE_ON_ERROR:

# Makefile specific settings
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
SAMTOOLS_DIR = /usr/bin
SAMTOOLS = $(SAMTOOLS_DIR)/samtools

# FastQC 
FASTQC_DIR := $(PROGRAMS)/FastQC
FASTQC := $(FASTQC_DIR)/fastqc
FASTQC_THREADS := 4

####################
### Dependencies ###
####################

# References
REFERENCE_DIR := ./reference
REFERENCE_BWA := $(REFERENCE_DIR)/bwa/reference.fa
REFERENCE := $(REFERENCE_DIR)/reference.fa

###################
### Input Files ###
###################

# Files to proces
FASTQ_EXTENSION := trimmed.fastq
LEFT_SUFFIX := _1
RIGHT_SUFFIX := _2

SAMPLE := $(shell ls *$(LEFT_SUFFIX).$(FASTQ_EXTENSION) | python -c 'import os; import sys; print os.path.commonprefix(list(sys.stdin)).split("_")[0]')
PAIRS := $(shell ls *$(LEFT_SUFFIX).$(FASTQ_EXTENSION) | sed 's/$(LEFT_SUFFIX).$(FASTQ_EXTENSION)//')
SINGLES := $(basename $(shell ls *$(LEFT_SUFFIX).$(FASTQ_EXTENSION) *$(RIGHT_SUFFIX).$(FASTQ_EXTENSION)))

###############
### Targets ###
###############

# Full pipeline 
all: fastqc alignment

# Partial recipies
fastqc:  $(addsuffix .fastqc, $(PAIRS))
alignment: $(addsuffix .sort.bam.bai, $(SAMPLE))

.PHONY: test

#########################
### Debug targets     ###
#########################

# Debugging variables
test:
	echo $(CURDIR)
	echo $(MAKEFILE_DIR)

#########################
### Rules and Recipes ###
#########################

# FastQC for quality control
%.fastqc: %$(LEFT_SUFFIX).$(FASTQ_EXTENSION) %$(RIGHT_SUFFIX).$(FASTQ_EXTENSION)
	mkdir -p $@ && (SGE_RREQ="-now no -pe $(SGE_PE) $(FASTQC_THREADS)" $(FASTQC) -q -t $(FASTQC_THREADS) -o $@ $^ || (rm -Rf $@ && false))

# BWA Alignment create .sai files from fastq files
%.sai: %.$(FASTQ_EXTENSION) %.$(FASTQ_EXTENSION)
	SGE_RREQ="-pe $(SGE_PE) $(BWA_OPTION_THREADS)" $(BWA) aln $(BWA_ALN_OPTIONS) -I $(REFERENCE_BWA) $< > $@

# BWA Alignment, create a samfile from two sai files from a paired end sample
%.sam: %$(LEFT_SUFFIX).sai %$(RIGHT_SUFFIX).sai %$(LEFT_SUFFIX).$(FASTQ_EXTENSION) %$(RIGHT_SUFFIX).$(FASTQ_EXTENSION)
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
	

