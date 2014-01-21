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

## Paths to tools used
DELLY_DIR = $(PROGRAMS_DIR)/delly_v0.0.9

NEW_DELLY := $(PROGRAMS_DIR)/delly/delly_v0.2.2_linux_x86_64bit

%.delly/delly.raw.vcf: %.bam $(REFERENCE)
	$(NEW_DELLY) t -t DEL -o $@ -g $(word 2, $^) $<

%.delly.vcf: %.delly/delly.raw.vcf
	cp $< $@





# for old version of delly (0.0.9)
##
#%.delly/reference.fa: $(REFERENCE)
#	mkdir -p $(dir $@);
#	cat $< | cut -f 1 -d' ' > $@

## 
#%.delly/delly.tsv: %.bam %.delly/reference.fa
#	## TODO the source of some of the input files is unclear
#	$(DELLY) -p -g $(word 2, $^) -b $(addprefix BREAKPOINT.txt, $(dir $@)) -o $@ $<

#%.delly.vcf: %.delly/delly.tsv
#	grep "Deletion" $< > $<.deletion.tab
#	perl $(THIS_MAKEFILE_DIR)/delly-extract-convert.pl $<.deletion.tab > $@

## I ran Delly on the Ler dataset from Bowtie2 using a 16 core virtual machine (ubuntu).  The following commands:
## 
## -    Deletions: ./delly
## •       Tandem duplications: ./duppy
## •       Inversions: ./invy
## •       Translocations: ./jumpy
## 
## cd ~/Desktop/delly_v0.0.9
## ./delly -p -g ~/Desktop/TAIR9-cleanheader.fa -b ~/Desktop/Delly-breakpoint-file.txt -o ~/Desktop/Delly.txt ~/Desktop/Ler-bt2.sort.bam
## ./duppy -p -g ~/Desktop/TAIR9-cleanheader.fa -b ~/Desktop/Delly-duppy-breakpoint-file.txt -o ~/Desktop/Delly-duppy.txt ~/Desktop/Ler-bt2.sort.bam
## ./invy -p -g ~/Desktop/TAIR9-cleanheader.fa -b ~/Desktop/Delly-invy-breakpoint-file.txt -o ~/Desktop/Delly-invy.txt ~/Desktop/Ler-bt2.sort.bam
## ./jumpy -p -g ~/Desktop/TAIR9-cleanheader.fa -b ~/Desktop/Delly-jumpy-breakpoint-file.txt -o ~/Desktop/Delly-jumpy.txt ~/Desktop/Ler-bt2.sort.bam
## 
## It does not appear that these need to be run sequentially, so they should be able to be run in parallel.
