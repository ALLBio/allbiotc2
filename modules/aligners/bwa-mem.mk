# Makefile - bwa module
#
# (c) 2013 - Wai Yi Leung

MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))
include $(MAKEFILE_DIR)/bwa-mem.conf.mk
include $(MAKEFILE_DIR)/../../conf.mk

# The target is .bam, we expect input: .fastq

%.sam: %$(PEA_MARK).$(FASTQ_EXTENSION) %$(PEB_MARK).$(FASTQ_EXTENSION)
	SGE_RREQ="-pe $(SGE_PE) $(THREADS)" $(BWA) mem -t $(THREADS) $(REFERENCE_BWA) $^ > $@

#%.sam: $(IN)
#	SGE_RREQ="-pe $(SGE_PE) $(THREADS)" $(BWA) mem -t $(THREADS) $(REFERENCE_BWA) $^ > $@

%.unsort.bam: %.sam
	$(SAMTOOLS) view -bST $(REFERENCE) -o $@ $<

%.bam: %.unsort.bam
	$(SAMTOOLS) sort $< $(basename $@)
