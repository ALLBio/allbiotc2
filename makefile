#!/usr/bin/make

#####
## Inputs
#####
REFERENCE = /virdir/Backup/reads_and_reference/reference/TAIR9_chr_all.fas
FOLDER = /virdir/Backup/reads_and_reference
FASTQ_PATTERN = $(FOLDER)/ERR031544_*.trimmed.fastq
FASTQ_FILES = $(wildcard $(FASTQ_PATTERN))

#####
## Products
#####
MAPPED_READS = $(FASTQ_FILES:%.fastq=%.bam)
RAW_FASTQC = $(FASTQ_FILES:%.fastq=%_raw_fastqc)
BAM_FASTQC = $(FASTQ_FILES:%.bam=%_raw_fastqc)

#####
## Invoke all
#####
all: $(RAW_FASTQC) $(BAM_FASTQC) 


#####
## Simple conversions based on file extensions
#####

## Generate raw FastQC reports
%_raw_fastqc: %.fastq
	mkdir $@; \
	fastqc --format fastq --noextract $? --outdir $@

## Generate mapped FastQC reports
%_mapped_fastqc: %.bam
	mkdir $@; \
	fastqc --format bam --noextract $? --outdir $@

## Sort bam file using Samtools
%.sort.bam: %.bam
	samtools sort $? $@;

## Convert sam to bam using samtools
%.bam: %.sam
	samtools view -S -b -o $@ $?

#####
## More complex tools to run
#####

## Build a bowtie index with --offrate=3
bowtie_build: $(REFERENCE)
	bowtie-build --offrate 3 $? $@
	touch $@

## Map reads from a fastq files to the bowtie index
%.sam: bowtie_build %.fastq
	bowtie -q --tryhard --sam --best --strata -k 1 -m 1 $? > $@


#####
## Call the SV files
#####

%.bd.vcf: %.bam
	make -f breakdancer/makefile -n $@


