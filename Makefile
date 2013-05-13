# preprocess-bwa.mk
#
# Makefile for preprocessing FastQ files -- Part of pipeline for ALLBioTC2
#
# (c) 2013 by Wai Yi Leung [SASC-LUMC]
# 
# Adapted makefile configuration from Wibowo Arindrarto [SASC-LUMC]

# Load all module definition
# Makefile specific settings
MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))
include $(MAKEFILE_DIR)/modules.mk
include $(MAKEFILE_DIR)/conf.mk

#######################
### General Targets ###
#######################

SAMPLE := $(shell ls *$(PEA_MARK).$(FASTQ_EXTENSION) | python -c 'import os; import sys; print os.path.commonprefix(list(sys.stdin)).split("_")[0]')
PAIRS := $(shell ls *$(PEA_MARK).$(FASTQ_EXTENSION) | sed 's/$(LEFT_SUFFIX).$(FASTQ_EXTENSION)//')
SINGLES := $(basename $(shell ls *$(PEA_MARK).$(FASTQ_EXTENSION) *$(PEB_MARK).$(FASTQ_EXTENSION)))

qc: $(addsuffix .fastqc, $(SINGLES))
BAM_FILES = $(addsuffix .bam, $(SAMPLE)) $(addsuffix .bam.bai, $(SAMPLE)) $(addsuffix .sam, $(SAMPLE))
alignment: $(addprefix $(OUT_DIR)/, $(BAM_FILES))
aligmentstats: $(addprefix $(OUT_DIR)/, $(addsuffix .flagstat, $(SAMPLE)) )

# creates the output directory
$(OUT_DIR):
	mkdir -p $@

%.fastqc: %.$(FASTQ_EXTENSION)
	$(MAKE) -f $(MAKEFILE_DIR)/modules/fastqc.mk $@

%.sam: %$(PEA_MARK).$(FASTQ_EXTENSION) %$(PEB_MARK).$(FASTQ_EXTENSION)
	$(MAKE) -f $(MAKEFILE_DIR)/modules/alignment.mk IN="$^" $@

%.bam: %$(PEA_MARK).$(FASTQ_EXTENSION) %$(PEB_MARK).$(FASTQ_EXTENSION)
	$(MAKE) -f $(MAKEFILE_DIR)/modules/alignment.mk IN="$^" $@

%.bam.bai: %$(PEA_MARK).$(FASTQ_EXTENSION) %$(PEB_MARK).$(FASTQ_EXTENSION)
	$(MAKE) -f $(MAKEFILE_DIR)/modules/alignment.mk IN="$^" $@

%.flagstat: %.bam
	$(MAKE) -f $(MAKEFILE_DIR)/modules/alignment.mk IN="$^" $@


.PHONY: clean

clean:
	rm -rf *.bam *.bai *.sam *.flagstat *.fastqc

###############
### Targets ###
###############

# outputdir for all recipies:

SV_PROGRAMS := gasv pindel delly prism bd
SV_OUTPUT = $(foreach s, $(SAMPLE), $(foreach p, $(SV_PROGRAMS), $(s).$(p).vcf))
sv_vcf: $(addprefix $(OUT_DIR)/, $(SV_OUTPUT))

# Partial recipies
FASTQC_FILES = $(addsuffix .raw_fastqc, $(PAIRS)) $(addsuffix .trimmed_fastqc, $(PAIRS))
fastqc: $(addprefix $(OUT_DIR)/, $(FASTQC_FILES))

all: fastqc alignment aligmentstats sv_vcf

.PHONY: test

#########################
### Debug targets     ###
#########################

# Debugging variables
test:
	echo $(CURDIR)
	echo $(MAKEFILE_DIR)
	echo $(SV_OUTPUT)

#########################
### Rules and Recipes ###
#########################

# FastQC for quality control
%.raw_fastqc: %$(LEFT_SUFFIX).$(FASTQ_EXTENSION) %$(RIGHT_SUFFIX).$(FASTQ_EXTENSION)
	mkdir -p $@ && (SGE_RREQ="-now no -pe $(SGE_PE) $(FASTQC_THREADS)" $(FASTQC) --format fastq -q -t $(FASTQC_THREADS) -o $@ $^ || (rm -Rf $@ && false))

%$(LEFT_SUFFIX).trimmed.$(FASTQ_EXTENSION) %$(RIGHT_SUFFIX).trimmed.$(FASTQ_EXTENSION): %$(LEFT_SUFFIX).$(FASTQ_EXTENSION) %$(RIGHT_SUFFIX).$(FASTQ_EXTENSION)
	$(SICKLE) pe -f $(word 1, $^) -r $(word 2, $^) -t sanger -o $(basename $(word 1, $^)).trimmed.fastq -p $(basename $(word 2, $^)).trimmed.fastq -s $(basename $(word 1, $^)).singles.fastq -q 30 -l 25 > $(basename $(word 1, $^)).filtersync.stats

# FastQC to check trimming
%.trimmed_fastqc: %$(LEFT_SUFFIX).trimmed.$(FASTQ_EXTENSION) %$(RIGHT_SUFFIX).trimmed.$(FASTQ_EXTENSION)
	mkdir -p $@ && (SGE_RREQ="-now no -pe $(SGE_PE) $(FASTQC_THREADS)" $(FASTQC) --format fastq -q -t $(FASTQC_THREADS) -o $@ $^ || (rm -Rf $@ && false))

## BWA Alignment create .sai files from fastq files
#%.sai: %.trimmed.$(FASTQ_EXTENSION)
#	SGE_RREQ="-pe $(SGE_PE) $(BWA_OPTION_THREADS)" $(BWA) aln $(BWA_ALN_OPTIONS) $(if $(findstring sanger, $(QSCORE_FORMAT)),,-I) $(REFERENCE_BWA) $< > $@

## BWA Alignment, create a samfile from two sai files from a paired end sample
#%.sam: %$(LEFT_SUFFIX).sai %$(RIGHT_SUFFIX).sai %$(LEFT_SUFFIX).trimmed.$(FASTQ_EXTENSION) %$(RIGHT_SUFFIX).trimmed.$(FASTQ_EXTENSION)
#	$(BWA) sampe $(BWA_SAMPE_OPTIONS) $(REFERENCE_BWA) $^ > $@

## SamTools view, convert sam to bam format
#%.unsort.bam: %.sam
#	$(SAMTOOLS) view -bST $(REFERENCE) -o $@ $<

## Samtools sort, sort the bamfile.
#%.sort.bam: %.unsort.bam
#	$(SAMTOOLS) sort $< $(basename $@)

## Samtools Flagstat
#%.flagstat: %.sort.bam
#	$(SAMTOOLS) flagstat $< > $@

## Samtools index
#%.sort.bam.bai: %.sort.bam
#	$(SAMTOOLS) index $<




#######################
## Call the SV files ##
#######################

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









