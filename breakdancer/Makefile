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

include $(MAKEFILE_DIR)/../conf.mk

BREAKDANCER_VERSION := breakdancer-v1.4.4
BREAKDANCER_CFG_VERSION := breakdancer-max1.4.4

## Paths to tools used
BREAKDANCER_DIR := $(PROGRAMS_DIR)/breakdancer/$(BREAKDANCER_VERSION)
BREAKDANCER_MAX := $(BREAKDANCER_DIR)/bin/breakdancer-max
BAM2CFG := $(BREAKDANCER_DIR)/lib/$(BREAKDANCER_CFG_VERSION)/bam2cfg.pl
BD2VCF := python $(THIS_MAKEFILE_DIR)/breakdancer2vcf.py

# Just for make -n
$(BDCFG):
	@

## Create the native tabular output file for breakdancer
%.breakdancer/bd.tsv: $(BDCFG)
	mkdir -p $(dir $@);
	$(BREAKDANCER_MAX) $< > $@

## Convert the native tabular file for breakdancer to variant call format file
%.breakdancer.vcf: %.breakdancer/bd.tsv
	$(BD2VCF) -i $< -o $@

.PHONY: install
## Tool installation
install:
	echo "Installing perl packages for breakdancer..."
	sudo cpan Statistics::Descriptive;
	sudo cpan GD::Graph::histogram;
	sudo cpan Math::CDF;

