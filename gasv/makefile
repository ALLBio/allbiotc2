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

# GASV
GASV_DIR := $(PROGRAMS_DIR)/gasv
BAM2GASV := $(GASV_DIR)/bin/BAMToGASV.jar
GASV := $(GASV_DIR)/bin/GASV.jar
JAVA := java -Xms512m -Xmx2048m -jar

GASVProHQ := $(GASV_DIR)/bin/GASVPro-HQ.sh
GASVPro := $(GASV_DIR)/bin/GASVPro.sh

GASV2VCF := python $(MAKEFILE_DIR)/gasv2vcf.py


###############
### Targets ###
###############

all: $(OUT)

#########################
### Rules and Recipes ###
#########################

# expect $(IN) = *.bam
%.gasv.in: %.sort.bam
	$(JAVA) $(BAM2GASV) $?
	##or with options
	# -MAPPING_QUALITY 30 -CUTOFF_LMINLMAX SD=3
	##or if multiple libraries:
	# -LIBRARY_SEPARATED all
	##output_file(s):
	## Ler-bt2.sort.bam.info,
	## Ler-bt2.sort.bam.gasv.in,
	## Ler-bt2.sort.bam_all.deletion,
	## Ler-bt2.sort.bam_all.insertion,
	## Ler-bt2.sort.bam_all.inversion,
	## Ler-bt2.sort.bam_all.divergent,
	## Ler-bt2.sort.bam_all.translocation

%.gasv.in.clusters: %.gasv.in
	$(JAVA) $(GASV) $?

%.gasv.vcf: %.gasv.in.clusters
    $(GASV2VCF) %< %@ bwa
