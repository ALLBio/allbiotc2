MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))
include $(MAKEFILE_DIR)/stampy.conf.mk
include $(MAKEFILE_DIR)/../../conf.mk

# The target is .bam, we expect input: .fastq

# Alignment with stampy
%.sam: %$(PEA_MARK).trimmed.$(FASTQ_EXTENSION) %$(PEB_MARK).trimmed.$(FASTQ_EXTENSION)
	(SGE_RREQ="-pe $(SGE_PE) $(THREADS)" $(STAMPY) -o $@ -g $(STAMPY_INDEX) -h $(STAMPY_HASH) --insertsize2=$(MP_INSERTSIZE) --insertsd2=$(MP_INSERTSIZE_SD) $(if $(findstring solexa,$(QSCORE_FORMAT)),--solexa) -t$(THREADS) --inputformat=fastq -M $^ )

# SAMTools
%.unsort.bam: %.sam
	$(SAMTOOLS) view -bST $(REFERENCE) -o $@ $<

%.bam: %.unsort.bam
	$(SAMTOOLS) sort $< $(basename $@)
