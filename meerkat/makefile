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

$(info $(MAKEFILE_DIR))

# VARIABLES:

THIS_DIR = $(shell pwd)
$(info $(THIS_DIR))

# meerkat 
MEERKAT_FOLDER := $(PROGRAMS_DIR)/Meerkat
MEERKAT_SCRIPTS := $(MEERKAT_FOLDER)/scripts
MEERKAT_BINS := $(MEERKAT_FOLDER)/bin
MEERKAT_SRC := $(MEERKAT_FOLDER)/src
MEERKAT_BAMTOOLSLIB := $(MEERKAT_SRC)/mybamtools/lib

$(info $(DATA_BAM))
OUTPUT_DIR := $(SAMPLE).meerkat/
# meerkat output files
MK_RAW_PREDICTIONS := $(addprefix $(OUTPUT_DIR), $(addsuffix .inter.refined.typ.sorted, $(SAMPLE)))
$(info $(MK_RAW_PREDICTIONS))
MK_COVERAGE_PDF := $(addprefix $(OUTPUT_DIR), $(addsuffix .pdf, $(SAMPLE)))
MK_VCF := $(addsuffix .meerkat.vcf, $(SAMPLE))
MK_VARIANTS := $(addprefix $(OUTPUT_DIR), $(addsuffix .variants, $(SAMPLE)))  
MK_VARIANTS_F:= $(addprefix $(OUTPUT_DIR), $(addsuffix .filtered.variants, $(SAMPLE)))

# RECEPIES
all: $(MK_VCF) $(MK_VARIANTS) $(MK_COVERAGE_PDF) $(MK_RAW_PREDICTIONS)

%.meerkat/$(SAMPLE).pdf: %.bam
	mkdir -p $(OUTPUT_DIR);
	ln -s -f $< $(OUTPUT_DIR)$(notdir $<);
	export LD_LIBRARY_PATH=$(MEERKAT_BAMTOOLSLIB); perl $(MEERKAT_SCRIPTS)/pre_process.pl -b $(OUTPUT_DIR)$(notdir $<) -I $(DATA_BWA_INDEXED_REF) -A $(DATA_FASTA_INDEX) -t $(DATA_THREADS) -S /usr/local/bin/

%.meerkat/$(SAMPLE).inter.refined.typ.sorted: %.bam %.meerkat/$(SAMPLE).pdf
	(SGE_RREQ="-now no -pe BWA 8" export LD_LIBRARY_PATH=$(MEERKAT_BAMTOOLSLIB); perl $(MEERKAT_SCRIPTS)/meerkat.pl -b $(OUTPUT_DIR)$(notdir $<) -F $(DATA_REFERENCE) -t $(DATA_THREADS) -B /usr/bin/ -Q 10)

%.meerkat/$(SAMPLE).variants: %.bam %.meerkat/$(SAMPLE).inter.refined.typ.sorted
	perl $(MEERKAT_SCRIPTS)/mechanism.pl -b $(OUTPUT_DIR)$(notdir $<) -R $(DATA_REPEAT_MASKER)

%.meerkat/$(SAMPLE).filtered.variants: %.meerkat/$(SAMPLE).variants %.bam
	perl $(MEERKAT_SCRIPTS)/filter_normal.pl -i $(OUTPUT_DIR)$(notdir $<) -o $@ -B $(lastword $^) -R $(DATA_REPEAT_MASKER) -Q 10

%.meerkat.vcf: %.meerkat/$(SAMPLE).filtered.variants
	perl $(MEERKAT_SCRIPTS)/meerkat2vcf.pl -i $< -o $@ -H $(DATA_HEADERFILE) -F $(DATA_REFERENCE)
	cp $@ ../


.PHONY: clean
clean:
	rm *.log *.gz *.rdist *.err *.pdf *.isinfo *.sai *.cl.* *.raw *.clusters *.discord *.mp.* *.bp.* *.sr.* 
