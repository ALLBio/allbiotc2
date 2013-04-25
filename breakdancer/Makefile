#!/usr/bin/make

# Makefile specific settings
THIS_MAKEFILE = $(firstword $(MAKEFILE_LIST))
MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))

#####################
### Used Programs ###
#####################

# Programs folder for custum software. 
PROGRAMS := /virdir/Scratch/software

## Paths to tools used
BREAKDANCER_DIR = $(PROGRAMS)/breakdancer_deploy_1.3.5
BREAKDANCER_MAX = $(BREAKDANCER_DIR)/bin/breakdancer-max
BAM2CFG = $(BREAKDANCER_DIR)/lib/breakdancer-max-unstable/bam2cfg.pl
BD2VCF = $(MAKEFILE_DIR)/breakdancer2vcf.py

## Create configuration file for Breakdancer based on bam file
%.bd.cfg: %.sort.bam
	perl $(BAM2CFG) $? > $@;

## Create the native tabular output file for breakdancer
%.bd.tsv: %.bd.cfg
	$(BREAKDANCER_MAX) $? > $@;

## Convert the native tabular file for breakdancer to variant call format file
%.bd.vcf: %.bd.tsv
	python $(BD2VCF) $?;

## Tool installation
install:
	# The following command require root privileges to install
    sudo cpan Statistics::Descriptive;
    sudo cpan GD::Graph::histogram;
    sudo cpan Math::CDF;
	#git clone git://github.com/genome/breakdancer.git
	#cd breakdancer; git checkout v1.3.6;
	#wget http://breakdancer.sourceforge.net/morecpp.html;
