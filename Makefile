# preprocess-bwa.mk
#
# Makefile for preprocessing FastQ files -- Part of pipeline for ALLBioTC2
#
# (c) 2013 by Wai Yi Leung [SASC-LUMC]
# 
# Adapted makefile configuration from Wibowo Arindrarto [SASC-LUMC]
# 
# This pipeline is able to run with multiple aligners (aligner modules)
#
# Directory structure:
# - input
# - scripts
# - run
#   |
#   - bwa-aln
#   - bwa-mem
#   - bt2
# 
# The pipeline will take care of the different aligners/folders




# Load all module definition
# Makefile specific settings
MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))
include $(MAKEFILE_DIR)/modules.mk
include $(MAKEFILE_DIR)/conf.mk

#######################
### General Targets ###
#######################

all: fastqc alignment aligmentstats sv_vcf

qc: $(addsuffix .fastqc, $(SINGLES))
BAM_FILES = $(addsuffix .sam, $(SAMPLE)) $(addsuffix .bam, $(SAMPLE)) $(addsuffix .bam.bai, $(SAMPLE))
alignment: $(addprefix $(OUT_DIR)/, $(BAM_FILES))
aligmentstats: $(addprefix $(OUT_DIR)/, $(addsuffix .flagstat, $(SAMPLE)) )

# creates the output directory
$(OUT_DIR):
	mkdir -p $@

%.fastqc: %.$(FASTQ_EXTENSION)
	$(MAKE) -f $(MAKEFILE_DIR)/modules/fastqc.mk $@

# filename = test_bla
# $(SAMPLE) = test
# prerequist = test.1.trimmed.fastq

%.sam: %$(PEA_MARK).trimmed.$(FASTQ_EXTENSION) %$(PEB_MARK).trimmed.$(FASTQ_EXTENSION)
	$(MAKE) -f $(MAKEFILE_DIR)/modules/alignment.mk IN="$^" $@

%.bam: %$(PEA_MARK).trimmed.$(FASTQ_EXTENSION) %$(PEB_MARK).trimmed.$(FASTQ_EXTENSION)
	$(MAKE) -f $(MAKEFILE_DIR)/modules/alignment.mk IN="$^" $@

%.bam.bai: %$(PEA_MARK).trimmed.$(FASTQ_EXTENSION) %$(PEB_MARK).trimmed.$(FASTQ_EXTENSION)
	$(MAKE) -f $(MAKEFILE_DIR)/modules/alignment.mk IN="$^" $@

%.flagstat: %.bam
	$(MAKE) -f $(MAKEFILE_DIR)/modules/alignment.mk IN="$^" $@


.PHONY: clean

clean:
	rm -rf *.bam *.bai *.sam *.flagstat *.fastqc *~

###############
### Targets ###
###############

# outputdir for all recipies:

SV_PROGRAMS := gasv delly bd prism pindel clever svdetect
SV_OUTPUT = $(foreach s, $(SAMPLE), $(foreach p, $(SV_PROGRAMS), $(s).$(p).vcf))
sv_vcf: $(addprefix $(OUT_DIR)/, $(SV_OUTPUT))

# Partial recipies
FASTQC_FILES = $(addsuffix .raw_fastqc, $(PAIRS)) $(addsuffix .trimmed_fastqc, $(PAIRS))
fastqc: $(addprefix $(OUT_DIR)/, $(FASTQC_FILES))


.PHONY: test

#########################
### Debug targets     ###
#########################

# Debugging variables
test:
	echo $(CURDIR)
	echo $(MAKEFILE_DIR)
	echo $(SV_OUTPUT)
	echo $(SAMPLE)

#########################
### Rules and Recipes ###
#########################

# FastQC for quality control
%.raw_fastqc: %$(PEA_MARK).$(FASTQ_EXTENSION) %$(PEB_MARK).$(FASTQ_EXTENSION)
	mkdir -p $@ && (SGE_RREQ="-now no -pe $(SGE_PE) $(FASTQC_THREADS)" $(FASTQC) --format fastq -q -t $(FASTQC_THREADS) -o $@ $^ || (rm -Rf $@ && false))

%$(PEA_MARK).trimmed.$(FASTQ_EXTENSION) %$(PEB_MARK).trimmed.$(FASTQ_EXTENSION): %$(PEA_MARK).$(FASTQ_EXTENSION) %$(PEB_MARK).$(FASTQ_EXTENSION)
	$(SICKLE) pe -f $(word 1, $^) -r $(word 2, $^) -t sanger -o $(basename $(word 1, $^)).trimmed.fastq -p $(basename $(word 2, $^)).trimmed.fastq -s $(basename $(word 1, $^)).singles.fastq -q 30 -l 25 > $(basename $(word 1, $^)).filtersync.stats

# FastQC to check trimming
%.trimmed_fastqc: %$(PEA_MARK).trimmed.$(FASTQ_EXTENSION) %$(PEB_MARK).trimmed.$(FASTQ_EXTENSION)
	mkdir -p $@ && (SGE_RREQ="-now no -pe $(SGE_PE) $(FASTQC_THREADS)" $(FASTQC) --format fastq -q -t $(FASTQC_THREADS) -o $@ $^ || (rm -Rf $@ && false))


##############################
## Call the SV applications ##
##############################

%.bd.vcf: %.bam
	$(MAKE) -C $(PWD) -f $(MAKEFILE_DIR)/breakdancer/Makefile REFERENCE=$(REFERENCE) $@

%.pindel.vcf: %.bam
	$(MAKE) -C $(PWD) -f $(MAKEFILE_DIR)/pindel/Makefile REFERENCE=$(REFERENCE) $@

%.delly.vcf: %.bam
	$(MAKE) -C $(PWD) -f $(MAKEFILE_DIR)/delly/Makefile REFERENCE=$(REFERENCE) $@

%.prism.vcf: %.bam
	$(MAKE) -C $(PWD) -f $(MAKEFILE_DIR)/prism/Makefile REFERENCE=$(REFERENCE) $@

%.gasv.vcf: %.bam
	$(MAKE) -C $(PWD) -f $(MAKEFILE_DIR)/gasv/makefile REFERENCE=$(REFERENCE) $@

%.clever.vcf: %.bam
	$(MAKE) -C $(PWD) -f $(MAKEFILE_DIR)/clever/Makefile REFERENCE=$(REFERENCE) IN=$< $@

%.svdetect.vcf: %.bam
	$(MAKE) -C $(PWD) -f $(MAKEFILE_DIR)/svdetect/makefile REFERENCE=$(REFERENCE) IN=$< $@









