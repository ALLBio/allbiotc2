# Makefile - BreakDancer-max Module for the AllBioTC2 pipeline
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

# Keep all files (Todo: In view of disk space, maybe we shouldn't do this?).
.SECONDARY:

# Delete target if recipe returns error status code.
.DELETE_ON_ERROR:

# Makefile specific settings
THIS_MAKEFILE = $(lastword $(MAKEFILE_LIST))
MAKEFILE_DIR := $(realpath $(dir $(realpath $(firstword $(MAKEFILE_LIST)))))
THIS_MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))

#####################
### Used Programs ###
#####################

# Programs folder for custum software. 
PROGRAMS_DIR := /virdir/Scratch/software

include $(MAKEFILE_DIR)/../conf.mk

## Paths to tools used
BREAKDANCER_DIR = $(PROGRAMS_DIR)/breakdancer_deploy_1.3.5
BREAKDANCER_MAX = $(BREAKDANCER_DIR)/bin/breakdancer-max
BAM2CFG = $(BREAKDANCER_DIR)/lib/breakdancer-max-unstable/bam2cfg.pl
BD2VCF = python $(THIS_MAKEFILE_DIR)/breakdancer2vcf.py

## Create configuration file for Breakdancer based on bam file
%.breakdancer/bd.cfg: %.bam
	mkdir -p $(dir $@);
	perl $(BAM2CFG) $? > $@;
	cp $@ .;

## Create the native tabular output file for breakdancer
%.breakdancer/bd.tsv: %.breakdancer/bd.cfg
	$(BREAKDANCER_MAX) $? > $@;

## Convert the native tabular file for breakdancer to variant call format file
%.bd.vcf: %.breakdancer/bd.tsv
	$(BD2VCF) $?; cp $(dir $<)bd.vcf $@

.PHONY: install
## Tool installation
install:
	echo "Installing perl packages for breakdancer..."
	sudo cpan Statistics::Descriptive;
	sudo cpan GD::Graph::histogram;
	sudo cpan Math::CDF;
	#git clone git://github.com/genome/breakdancer.git
	#cd breakdancer; git checkout v1.3.6;
	#wget http://breakdancer.sourceforge.net/morecpp.html;
