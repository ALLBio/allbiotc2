# Makefile - Pindel module for the AllBioTC2 pipeline
#
# (c) 2013 - Wai Yi Leung
# (c) 2013 AllBio (see AUTHORS file)

########################
### Pipeline Setting ###
########################

# SGE configuration.
SGE_PE = BWA

# Keep all files (Todo: In view of disk space, maybe we shouldn't do this?).
.SECONDARY:

# Delete target if recipe returns error status code.
#.DELETE_ON_ERROR:

# Makefile specific settings
THIS_MAKEFILE = $(lastword $(MAKEFILE_LIST))
MAKEFILE_DIR := $(realpath $(dir $(realpath $(firstword $(MAKEFILE_LIST)))))
THIS_MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))

#####################
### Used Programs ###
#####################

include $(MAKEFILE_DIR)/../conf.mk

# Breakdancer
BREAKDANCER_VERSION := breakdancer-v1.4.4
BREAKDANCER_CFG_VERSION := breakdancer-max1.4.4

## Paths to tools used
BREAKDANCER_DIR := $(PROGRAMS_DIR)/breakdancer/$(BREAKDANCER_VERSION)
BAM2CFG := $(BREAKDANCER_DIR)/lib/$(BREAKDANCER_CFG_VERSION)/bam2cfg.pl

# pindel 
PINDEL_VERSION := pindel-0.2.5
PINDEL_DIR := $(PROGRAMS_DIR)/pindel/$(PINDEL_VERSION)
PINDEL := $(PINDEL_DIR)/pindel
PINDEL2VCF := $(PINDEL_DIR)/pindel2vcf
PINDEL_THREADS = $(THREADS)
PINDEL_OUTPUT_EXTENTIONS := .pindel_D .pindel_SI .pindel_LI .pindel_INT .pindel_INV .pindel_TD
PINDEL_TOVCF_EXTENSION := .pindel_D .pindel_SI .pindel_INV .pindel_TD


###############
### Targets ###
###############

all: $(OUT)


#########################
### Rules and Recipes ###
#########################


# Just for make -n
$(BDCFG):
	echo $(BDCFG)
%.bam:
	@
%.bam.bai:
	@

%.pindel/bd.cfg: %.bam %.bam.bai
	mkdir -p $(dir $@);
	$(BAM2CFG) $< > $@

# Pindel
%.pindel/pindel.cfg: %.bam $(BDCFG)
	mkdir -p $(dir $@);
	(PINDEL_INSERTSIZE=`sed -e 's/\t/\n/g' $(lastword $^) | grep mean: | cut -f 2 -d ':'`;echo '$<	'$$PINDEL_INSERTSIZE'	$<' > $@)


# Turning off the Interchromosomal translocation detection by : -I 0
# Turning off the Inversion detection: -r 0
# Turning off the tandem duplication: -t 0
# Enable long insertion : -l 1
%.pindel/pindel_res: %.pindel/pindel.cfg %.bam %.bam.bai
	SGE_RREQ="-now no -pe $(SGE_PE) $(PINDEL_THREADS)" $(PINDEL) -f $(REFERENCE) -i $< -o $@ -I 0 -r 0 -t 0 -l 1 -T $(PINDEL_THREADS) && touch $@

%.pindel.vcf: %.pindel/pindel_res
	$(PINDEL2VCF) -P $< -r $(REFERENCE) -R benchmarkgenome -d $(shell date +'%Y%m%d%H%M%S') -v $@

.PHONY: install
## Tool installation
install:
	sudo cpan Statistics::Descriptive;
	sudo cpan GD::Graph::histogram;
	sudo cpan Math::CDF;

