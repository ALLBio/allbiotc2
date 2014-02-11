# Makefile :: SVDetect module for SV-benchmarking
#
# (c) 2013 by Wai Yi Leung [SASC-LUMC]
# AllBio Hackathon

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
#.DELETE_ON_ERROR:

# Makefile specific settings
MAKEFILE_DIR := $(realpath $(dir $(realpath $(firstword $(MAKEFILE_LIST)))))
THIS_MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))

#####################
### Used Programs ###
#####################

# programs folder for custom software.
PROGRAMS_DIR := /virdir/Scratch/software

include $(MAKEFILE_DIR)/../conf.mk

# SVDetect
SVDETECT_VERSION := SVDetect_r0.8b
SVDETECT_DIR := $(PROGRAMS_DIR)/svdetect/$(SVDETECT_VERSION)
SVDETECT_LIB_DIR := $(SVDETECT_DIR)/lib

SVDETECT := $(SVDETECT_DIR)/bin/SVDetect
SVDETECT_BAMPROCESSING := perl $(SVDETECT_DIR)/scripts/BAM_preprocessingPairs.pl
SVDETECT2VCF := python $(THIS_MAKEFILE_DIR)/svdetect2vcf.py
CREATE_CONFIG := bash $(THIS_MAKEFILE_DIR)/create_conf.sh

###############
### Targets ###
###############

all: $(OUT)

#########################
### Rules and Recipes ###
#########################

# expect $(IN) = *.bam

# Just for make -n
%.sam:
	@
	
# print the chromosome sizes to svdetect fasta index.
%.svdetect.fai: $(REFERENCE).fai
	awk '{print NR,$$1,$$2}' $< >$@

# for the sake of clean working directories, rename original filename to sample.bam in svdetect workdir

%.svdetect/.workdir: %.sam
	mkdir -p $(dir $@) && touch $@;

%.svdetect/sample.bam: %.sam %.svdetect/.workdir
	$(SAMTOOLS) view -bS -o $@ -@ $(THREADS) $< 

%.svdetect/sample.ab.bam: %.svdetect/sample.bam
	$(SVDETECT_BAMPROCESSING) -o $(dir $@) $< > $(addsuffix stats.txt, $(dir $@) ) 2>&1
%.svdetect/stats.txt: %.svdetect/sample.bam
	@

%.svdetect/sample.sv.conf: %.svdetect/stats.txt %.svdetect.fai %.svdetect/sample.ab.bam
	$(CREATE_CONFIG) -s $< -o $@ -r $(word 2, $^) -b $(word 3, $^) -t $(THREADS) -d $(dir $@)results -e $(dir $@)tmp

%.svdetect/results/sample.ab.bam.all.links.filtered: %.svdetect/sample.ab.bam %.svdetect/sample.sv.conf
	SGE_RREQ="-now no -pe $(SGE_PE) $(THREADS)" export PERL5LIB=$(SVDETECT_LIB_DIR):$$PERL5LIB;$(SVDETECT) linking filtering -conf $(lastword $^)

%.svdetect/results/sample.ab.bam.all.links.filtered.sv.txt: %.svdetect/results/sample.ab.bam.all.links.filtered %.svdetect/sample.sv.conf
	SGE_RREQ="-now no -pe $(SGE_PE) $(THREADS)" export PERL5LIB=$(SVDETECT_LIB_DIR):$$PERL5LIB;$(SVDETECT) links2SV -conf $(lastword $^)

%.svdetect.vcf: %.svdetect/results/sample.ab.bam.all.links.filtered.sv.txt $(REFERENCE)
	$(SVDETECT2VCF) -f $< -r $(lastword $^)  | sort -k1,1n -k2,2n > $@
