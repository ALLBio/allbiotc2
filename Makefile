# Makefile - main file for the AllBioTC2 pipeline
#
# (c) 2013 - Wai Yi Leung
# (c) 2013 AllBio (see AUTHORS file)
# 
# Adapted makefile configuration from Wibowo Arindrarto [SASC-LUMC]
# 
# This pipeline is able to run with multiple aligners (aligner modules)
# Settings can be found in the conf.mk in this directory

# Load all module definition
# Makefile specific settings
MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))
THIS_MAKEFILE := $(lastword $(MAKEFILE_LIST))
.ONESHELL:
SHELL := $(MAKEFILE_DIR)/modules/logwrapper.sh
include $(MAKEFILE_DIR)/modules.mk
include $(MAKEFILE_DIR)/conf.mk
export MAKEFILE_DIR THIS_MAKEFILE

#MAKE := /data/DIV5/SASC/common/programs/sge/shake
MAKE := make
#######################
#### Basic testing  ###
#######################

# only check the variable in non-install goals
ifneq ($(MAKECMDGOALS),install)
$(if $(REFERENCE_VCF),,$(error REFERENCE_VCF is a required value))
endif
ifeq ($(MAKECMDGOALS),preprocess)
$(if $(SDI_FILE),,$(error SDI_FILE is a required value))
endif


#######################
### General Targets ###
#######################

all: fastqc trimming alignment aligmentstats sv_vcf report

##############################
### Generate reference VCF ###
##############################

ifeq ($(MAKECMDGOALS),preprocess)
preprocess: $(REFERENCE_VCF)
$(REFERENCE_VCF): $(SDI_FILE)
	$(PYTHON_EXE) $(MAKEFILE_DIR)/sdi-to-vcf/sdi-to-vcf.py -p $^ $(REFERENCE) > $@
endif

###############
### Targets ###
###############

# outputdir for all recipies:

SV_PROGRAMS := gasv delly breakdancer pindel clever svdetect
SV_OUTPUT := $(foreach s, $(SAMPLE), $(foreach p, $(SV_PROGRAMS), $(s).$(p).vcf))
sv_vcf: $(addprefix $(OUT_DIR)/, $(SV_OUTPUT))

# Partial recipies
qc: $(addsuffix .fastqc, $(SINGLES))
TRIMMED_FASTQ_FILES := $(addsuffix .trimmed.$(FASTQ_EXTENSION), $(SINGLES))
trimming: $(TRIMMED_FASTQ_FILES)
FASTQC_FILES := $(addsuffix .raw_fastqc, $(PAIRS)) $(addsuffix .trimmed_fastqc, $(PAIRS))
fastqc: $(addprefix $(OUT_DIR)/, $(FASTQC_FILES))
report: $(addprefix $(OUT_DIR)/, $(addsuffix .report.pdf, $(SAMPLE)))

# settings for reporting
EVALUATE_PREDICTIONS := $(PYTHON_EXE) $(MAKEFILE_DIR)/evaluation/evaluate-sv-predictions2


#########################
### Debug targets     ###
#########################

.PHONY: test

# Debugging variables
test:
	echo $(CURDIR)
	echo $(MAKEFILE_DIR)
	echo $(SV_OUTPUT)
	echo $(SAMPLE)

#########################
### Rules and Recipes ###
#########################

# creates the output directory
$(OUT_DIR):
	mkdir -p $@

%.fastqc: %.$(FASTQ_EXTENSION)
	$(MAKE) -f $(MAKEFILE_DIR)/modules/fastqc.mk $@

# FastQC for quality control
%.raw_fastqc: %$(PEA_MARK).$(FASTQ_EXTENSION) %$(PEB_MARK).$(FASTQ_EXTENSION)
	mkdir -p $@ && (SGE_RREQ="-now no -pe $(SGE_PE) $(FASTQC_THREADS)" $(FASTQC) --format fastq -q -t $(FASTQC_THREADS) -o $@ $^ || (rm -Rf $@ && false))

%$(PEA_MARK).trimmed.$(FASTQ_EXTENSION): %$(PEA_MARK).$(FASTQ_EXTENSION) %$(PEB_MARK).$(FASTQ_EXTENSION)
	$(SICKLE) pe -f $(word 1, $^) -r $(word 2, $^) -t sanger -o $(basename $(word 1, $^)).trimmed.$(FASTQ_EXTENSION) -p $(basename $(word 2, $^)).trimmed.$(FASTQ_EXTENSION) -s $(basename $(word 1, $^)).singles.$(FASTQ_EXTENSION) -q 30 -l 25 > $(basename $(word 1, $^)).filtersync.stats
%$(PEB_MARK).trimmed.$(FASTQ_EXTENSION): 
	@


# FastQC to check trimming
%.trimmed_fastqc: %$(PEA_MARK).trimmed.$(FASTQ_EXTENSION) %$(PEB_MARK).trimmed.$(FASTQ_EXTENSION)
	mkdir -p $@ && (SGE_RREQ="-now no -pe $(SGE_PE) $(FASTQC_THREADS)" $(FASTQC) --format fastq -q -t $(FASTQC_THREADS) -o $@ $^ || (rm -Rf $@ && false))

#################
### Alignment ###
#################

BAM_FILES := $(addsuffix .sam, $(SAMPLE)) $(addsuffix .bam, $(SAMPLE)) $(addsuffix .bam.bai, $(SAMPLE))
alignment: $(addprefix $(OUT_DIR)/, $(BAM_FILES))
aligmentstats: $(addprefix $(OUT_DIR)/, $(addsuffix .flagstat, $(SAMPLE)) )

%.sam: %$(PEA_MARK).trimmed.$(FASTQ_EXTENSION) %$(PEB_MARK).trimmed.$(FASTQ_EXTENSION)
	$(MAKE) -C $(PWD) -f $(MAKEFILE_DIR)/modules/alignment.mk $@

%.bam: %$(PEA_MARK).trimmed.$(FASTQ_EXTENSION) %$(PEB_MARK).trimmed.$(FASTQ_EXTENSION)
	@

%.bam.bai: %$(PEA_MARK).trimmed.$(FASTQ_EXTENSION) %$(PEB_MARK).trimmed.$(FASTQ_EXTENSION)
	@

%.flagstat: %.bam
	@


##############################
## Call the SV applications ##
##############################

get_extension = $(lastword $(subst ., , $(basename $(value 1))))

.SECONDEXPANSION:
%.vcf: $$(basename $$(basename $$@ )).bam
	$(MAKE) -C $(PWD) -f $(MAKEFILE_DIR)/$(call get_extension, $@)/Makefile REFERENCE=$(REFERENCE) $@

##############################
## Create comparison report ##
##############################

%.report.tex: $(SV_OUTPUT)
	$(EVALUATE_PREDICTIONS) -L $(REFERENCE_VCF) $^ > $@

%.report.pdf: %.report.tex
	pdflatex $^ && pdflatex $^


####################################
### Install software requirement ###
####################################
.PHONY: install

.SILENT:
install:
	echo Install python packages for the pipeline
	sudo apt-get install python-biopython
	$(foreach program, $(SV_PROGRAMS), $(MAKE) -C $(PWD) -f $(MAKEFILE_DIR)/$(program)/Makefile install)

.PHONY: help
help:
	echo ALLBio pipeline

.PHONY: clean

clean:
	rm -rf *.bam *.bai *.sam *.flagstat *.fastqc *~
