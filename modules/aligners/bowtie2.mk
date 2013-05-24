MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))
include $(MAKEFILE_DIR)/bowtie2.conf.mk
include $(MAKEFILE_DIR)/../../conf.mk

# The target is .bam, we expect input: .fastq

%.sam: %$(PEA_MARK).trimmed.$(FASTQ_EXTENSION) %$(PEB_MARK).trimmed.$(FASTQ_EXTENSION)
	SGE_RREQ="-pe $(SGE_PE) $(THREADS)" $(BOWTIE2) --quiet --local --met-file $(addsuffix bt2.metrics, $(basename $@) ) -x $(REFERENCE_BOWTIE2) -p $(THREADS) -1 $(firstword $^) -2 $(lastword $^) -S $@

%.unsort.bam: %.sam
	$(SAMTOOLS) view -bST $(REFERENCE) -o $@ $<

%.bam: %.unsort.bam
	$(SAMTOOLS) sort $< $(basename $@)
