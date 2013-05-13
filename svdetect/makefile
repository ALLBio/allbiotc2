#!/usr/bin/make

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

# programs folder for custom software.
PROGRAMS_DIR := /virdir/Scratch/software

# SVDetect
SVDETECT_DIR := $(PROGRAMS_DIR)/SVDetect_r0.8b
SVDETECT := $(SVDETECT_DIR)/bin/SVDetect
SVDETECT_BAMPROCESSING := perl $(SVDETECT_DIR)/lib/BAM_preprocessingPairs.pl
SVDETECT2VCF := python $(MAKEFILE_DIR)/svdetect2vcf.py

###############
### Targets ###
###############

all: $(OUT)

#########################
### Rules and Recipes ###
#########################

# expect $(IN) = *.bam

# print the chromosome sizes to svdetect fasta index.
%.svdetect.fai: $(REFERENCE).fai
	awk '{print $1,$1,$2}' $< >$@

%.sort.ab.bam: %.bam
	$(SVDETECT_BAMPROCESSING) $<

%.
	$(SVDETECT) linking filtering -conf ler.sv.conf 

%.svdetect.vcf: %.all.links.filtered.sv.txt
	$(SVDETECT2VCF) %< %@ BWA
