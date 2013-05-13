include modules/bwa.conf.mk
include conf.mk

# The target is .bam, we expect input: .fastq

%.sai: %.$(FASTQ_EXTENSION)
	SGE_RREQ="-pe $(SGE_PE) $(THREADS)" $(BWA) aln -t $(THREADS) $(if $(findstring solexa,$(QSCORE_FORMAT)),-I) -f $@ $(REFERENCE_BWA) $<

%.sam: %$(PEA_MARK).sai %$(PEB_MARK).sai %$(PEA_MARK).$(FASTQ_EXTENSION) %$(PEB_MARK).$(FASTQ_EXTENSION)
	$(BWA) sampe $(REFERENCE_BWA) -f $@ $^

%.unsort.bam: %.sam
	$(SAMTOOLS) view -bST $(REFERENCE) -o $@ $<

%.bam: %.unsort.bam
	$(SAMTOOLS) sort $< $(basename $@)
