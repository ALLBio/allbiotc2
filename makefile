#!/usr/bin/make

#####
## Inputs
#####
REFERENCE = /virdir/Backup/reads_and_reference/reference/TAIR9_chr_all.fas
FOLDER = /virdir/Backup/reads_and_reference
FASTQ_PATTERN = $(FOLDER)/*.trimmed.fastq
FASTQ_FILES = $(wildcard $(FASTQ_PATTERN))

#####
## Products
#####
MAPPED_READS = $(FASTQ_FILES:%.fastq=%.bam)
RAW_FASTQC = $(FASTQ_FILES:%.fastq=%_raw_fastqc)
#BAM_FASTQC = $(FASTQ_FILES:%.bam=%_raw_fastqc)
BAM_BT2_FASTQC = $(FASTQ_FILES:%.bowtie.bam=%_raw_fastqc)

#####
## Invoke all
#####
all: $(RAW_FASTQC) $(BAM_FASTQC) 

.PHONY: test

test:
	$(FASTQ_FILES)
#####
## Simple conversions based on file extensions
#####

## Generate raw FastQC reports
%_raw_fastqc: %.fastq
	mkdir $@; \
	fastqc --format fastq $? --outdir $@

## Generate mapped FastQC reports
%_mapped_fastqc: %.bam
	mkdir $@; \
	fastqc --format bam $? --outdir $@

## Sort bam file using Samtools
%.sort.bam: %.bam
	samtools sort $? $@;
	samtools index $@;

## Convert sam to bam using samtools
%.bam: %.sam
	samtools view -S -b -o $@ $?

#####
## More complex tools to run
#####

## Build a bowtie index with --offrate=3
bowtie_build: $(REFERENCE)
	bowtie-build --offrate 3 $< $<
	touch $@

## Map reads from a fastq files to the bowtie index
%.bowtie.sam: bowtie_build %_1.trimmed.fastq %_2.trimmed.fastq
	## TODO Use variables below instead of fixed paths
	bowtie2 -p 8 -t --un-conc $(basename).unmap.fa  -x $(REFERENCE) -1 $(word 2 $^) -2 $(word 3 $^) -S $@

#####
## Call the SV files
#####

%.bd.vcf: %.bam
	cd breakdancer && $(MAKE) $@

%.pindel.vcf: %.bam
	cd pindel && $(MAKE) IN=$< OUT=$@
