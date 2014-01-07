# Makefile - alignment for the AllBioTC2 pipeline
#
# (c) 2013 - Mateusz Kuzak
# (c) 2013 AllBio (see AUTHORS file)

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

# Programs
PROGRAMS_DIR := /virdir/Scratch/software

include $(MAKEFILE_DIR)/../conf.mk

# Prism
PRISM_DIR := $(PROGRAMS_DIR)/PRISM_1_1_6
PRISM := $(PRISM_DIR)/toolkit/run_PRISM.sh
PRISM2VCF := python $(THIS_MAKEFILE_DIR)/prism2vcf.py

###############
### Targets ###
###############

all: $(OUT)


#########################
### Rules and Recipes ###
#########################

# expect $(IN) = %.bam
%.prism/split_all.sam_ns_rmmul_cigar_sorted_sv: %.sam $(REFERENCE) bd.cfg
	mkdir -p $(dir $@);
	(export PRISM_PATH=$(PRISM_DIR);PRISM_INSERTSIZE=`sed -e 's/\t/\n/g' $(lastword $^) | grep mean: | cut -f 2 -d ':' | python -c "print '%d' % round(float(raw_input()),0)"`; PRISM_INSERTSIZESD=`sed -e 's/\t/\n/g' $(lastword $^) | grep std: | cut -f 2 -d ':' | python -c "print '%d' % round(float(raw_input()),0)"`;$(PRISM) -m $$PRISM_INSERTSIZE -e $$PRISM_INSERTSIZESD -I $(dir $@) -O $(dir $@) -r $(REFERENCE) -i $< -a BWA)

%.prism.vcf: %.prism/split_all.sam_ns_rmmul_cigar_sorted_sv
	$(PRISM2VCF) -f $< -o $@

## Tool installation
install:
	# prism howto is available at:
	# http://compbio.cs.toronto.edu/prism/PRISM_README
	wget http://compbio.cs.toronto.edu/prism/releases/PRISM_1_1_6.linux.x86_64.tar.gz
	tar xvzf PRISM_1_1_6.linux.x86_64.tar.gz 
	cd PRISM_1_1_6
	make
	export PRISM_PATH=$PWD

