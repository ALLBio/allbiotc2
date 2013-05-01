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
THIS_MAKEFILE = $(firstword $(MAKEFILE_LIST))
MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))

#####################
### Used Programs ###
#####################

# Programs
PROGRAMS_DIR := /virdir/Scratch/software

# Breakdancer
BREAKDANCE_DIR := $(PROGRAMS_DIR)/breakdancer_deploy_1.3.5
BREAKDANCE := $(BREAKDANCE_DIR)/bin/breakdancer-max
BREAKDANCE_BAM2CFG := perl $(BREAKDANCE_DIR)/lib/breakdancer-max-unstable/bam2cfg.pl

# pindel 
PINDEL_DIR := $(PROGRAMS_DIR)/pindel/trunk
PINDEL := $(PINDEL_DIR)/pindel
PINDEL2VCF := $(PINDEL_DIR)/pindel2vcf
PINDEL_THREADS = 8
PINDEL_OUTPUT_EXTENTIONS := .pindel_D .pindel_SI .pindel_LI .pindel_INT .pindel_INV .pindel_TD
PINDEL_TOVCF_EXTENSION := .pindel_D .pindel_SI .pindel_INV .pindel_TD


###############
### Targets ###
###############

all: $(OUT)


#########################
### Rules and Recipes ###
#########################

# expect $(IN) = %.sort.bam
# Breakdancer configfile generation
%.bd.cfg: $(IN) $(IN).bai
	$(BREAKDANCE_BAM2CFG) $< > $@

# Pindel
%.pindel.cfg: *.sort.bam %.bd.cfg
	(PINDEL_INSERTSIZE=`sed -e 's/\t/\n/g' $(lastword $^) | grep mean | cut -f 2 -d ':'`;echo -e '$<\t'$$PINDEL_INSERTSIZE'\t$<' > $@)

%.pindel: %.pindel.cfg %.sort.bam %.sort.bam.bai
	SGE_RREQ="-now no -pe $(SGE_PE) $(PINDEL_THREADS)" $(PINDEL) -f $(REFERENCE) -i $< -o $@  -I -T $(PINDEL_THREADS) && touch $@

.SECONDEXPANSION:
%.pindel.vcf: %.pindel
	$(PINDEL2VCF) -P $< -r $(REFERENCE) -R benchmarkgenome -d $(shell date +'%Y%m%d%H%M%S')

## Tool installation
install:
	sudo cpan Statistics::Descriptive;
	sudo cpan GD::Graph::histogram;
	sudo cpan Math::CDF;
	#git clone git://github.com/genome/breakdancer.git
	#cd breakdancer; git checkout v1.3.6;
	#wget http://breakdancer.sourceforge.net/morecpp.html;
