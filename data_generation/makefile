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
DATA_DIR := ./$(DATA_PREFIX)_$(DATASET).data


# Tool configuration

GENOMESIMULATOR = python $(THIS_MAKEFILE_DIR)/genomesimulator_final.py
SIMSEQ = java -Xmx2048m -jar $(PROGRAMS_DIR)/simseq-git/SimSeqNBProject/store/SimSeq.jar
SAM2FASTQ = python $(THIS_MAKEFILE_DIR)/sam2fastq.py
MAPPING_Q_1 = $(THIS_MAKEFILE_DIR)/hiseq_mito_default_bwa_mapping_mq10_1.txt
MAPPING_Q_2 = $(THIS_MAKEFILE_DIR)/hiseq_mito_default_bwa_mapping_mq10_2.txt

#ouput files
FASTQ := $(DATA_PREFIX)_$(DATASET)$(PEA_MARK).$(FASTQ_EXTENSION) $(DATA_PREFIX)_${DATASET}$(PEB_MARK).$(FASTQ_EXTENSION)
FASTA_FILE := $(DATA_DIR)/$(DATA_PREFIX)_$(DATASET).fasta
SAM_FILE := $(DATA_DIR)/$(DATA_PREFIX)_$(DATASET).sam.gz
$(info $(FASTQ))
OUTPUT = $(FASTA_FILE) $(SAM_FILE) $(FASTQ)

all: $(OUTPUT)

%.data/$(DATA_PREFIX)_$(DATASET).fasta: 
	mkdir -p $(DATA_DIR);
	$(GENOMESIMULATOR) $(REFERENCE_VCF) $(REFERENCE) $(DATA_DIR)/;
	cat $(DATA_DIR)/*.fasta > $@

%.data/$(DATA_PREFIX)_$(DATASET).sam.gz: %.data/$(DATA_PREFIX)_$(DATASET).fasta
	$(SIMSEQ) -1 $(READLENGTH) -2 $(READLENGTH) --error $(MAPPING_Q_1) --error2 $(MAPPING_Q_2) --insert_size $(INSERT_SIZE) --insert_stdev $(SD) --read_number ${READCOUNT} --read_prefix sim_ --reference $< --duplicate_probability $(DUPLICATE) --out /dev/stdout | gzip > $(SAM_FILE);

%.1.fastq: %.data/$(DATA_PREFIX)_$(DATASET).sam.gz	
	zcat $< | $(SAM2FASTQ) -s $(FASTQ);
	
%.2.fastq: %.1.fastq
	#just check if second fastq file is present
	test -e $@
