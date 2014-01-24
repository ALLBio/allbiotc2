# Makefile - Clever module for the AllBioTC2 pipeline
#
# (c) 2013 - Wai Yi Leung
# (c) 2013 AllBio (see AUTHORS file)

########################
### Pipeline Setting ###
########################

# SGE configuration.
SGE_PE := BWA

# Keep all files (Todo: In view of disk space, maybe we shouldn't do this?).
.SECONDARY:

# Delete target if recipe returns error status code.
.DELETE_ON_ERROR:

# Makefile specific settings
THIS_MAKEFILE := $(lastword $(MAKEFILE_LIST))
MAKEFILE_DIR := $(realpath $(dir $(realpath $(firstword $(MAKEFILE_LIST)))))
THIS_MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))

#####################
### Used Programs ###
#####################

include $(MAKEFILE_DIR)/../conf.mk

# clever-sv
CLEVER_VERSION := clever-toolkit-v2.0rc3
CLEVER_DIR := $(PROGRAMS_DIR)/clever/$(CLEVER_VERSION)/bin
CLEVER := $(CLEVER_DIR)/clever


###############
### Targets ###
###############

all: $(OUT)

#########################
### Rules and Recipes ###
#########################

# Just for make -n
%.bam:
	@
%.bam.bai:
	@

%.clever/predictions.vcf: %.bam
	mkdir -p $(dir $@);
	SGE_RREQ="-now no -pe $(SGE_PE) $(THREADS)" $(CLEVER) -f --use_xa --sorted -T $(THREADS) -k $< $(REFERENCE) $(dir $@); 

%.clever.vcf: %.clever/predictions.vcf
	cp $< $@

.PHONY: install
## Tool installation
install:
	sudo apt-get install libboost-all-dev
	sudo pip install SciPy bitarray
