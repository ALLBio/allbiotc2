MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))
THIS_MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))
include $(THIS_MAKEFILE_DIR)/../../conf.mk

%.unsort.bam: %$(PEA_MARK).$(FASTQ_EXTENSION) %$(PEB_MARK).$(FASTQ_EXTENSION)
	echo $(shell pwd)
	$(shell export PATH="/usr/local/bwa/current:"$$PATH ;\
	$(LASER) $(REFERENCE_BWA) $^ $(OUT_DIR)/$(DATA_PREFIX)_$(DATASET) -T 4)

%.bam: %.unsort.bam
	$(SAMTOOLS) sort $< $(basename $@)

%.bam.bai: %.bam
	$(SAMTOOLS) index $<

%.sam: %.bam
	$(SAMTOOLS) view -h -o $@ $<

.PHONY: test

test:
	$(shell pwd)
