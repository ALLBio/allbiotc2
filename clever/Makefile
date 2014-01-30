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

# clever
CLEVER_DIR := $(PROGRAMS_DIR)/clever$(VERSION)/bin
CLEVER := $(CLEVER_DIR)/clever


###############
### Targets ###
###############

all: $(OUT)


#########################
### Rules and Recipes ###
#########################

# expect $(IN) = %.bam
# Clever expects an sorted bam on names (this actually requires the unsorted sam file)
#%.clever/clever.bam: $(IN)
#	mkdir -p $(dir $@);
#	samtools view -bST $(REFERENCE) $(addsuffix .sam, $(basename $<)) > $@

%.clever.vcf: $(IN)
	mkdir -p $(basename $<).clever/;
	SGE_RREQ="-now no -pe $(SGE_PE) $(THREADS)" $(CLEVER) -f --use_xa --sorted -T $(THREADS) -k $< $(REFERENCE) $(basename $<).clever/; cp $(basename $<).clever/predictions.vcf $@

.PHONY: install
## Tool installation
install:
	sudo apt-get install libboost-all-dev
	sudo pip install SciPy
