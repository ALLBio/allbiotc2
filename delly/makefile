#!/usr/bin/make


## Paths to tools used
FOLDER=/virdir/Scratch/software/delly_v0.0.9/
DELLY=$(FOLDER)delly
DUPPY=$(FOLDER)duppy
INVY=$(FOLDER)invy
JUMPY=$(FOLDER)jumpy

##
%.cleanheader.fa: %.fasta 
	## TODO Insert code that cleaned the fasta headers
	## Of note is that the reference fasta file had to be modified so as to reduce the headers to exclude any commenting past the first space in the header. Once this was done, the program ran relatively quickly.
	

## 
%.delly.tsv: %.bam
	## TODO the source of some of the input files is unclear
	#$(DELLY) -p -g CLEANHEADER.fa -b BREAKPOINT.txt -o $@ $?
	#grep "Deletion" bwa-Delly-deletions.txt > bwa-Delly-deletions-list.tab
	# perl delly-extract-convert.pl bwa-Delly-deletions-list.tab > Delly-bwa.vcf

%.duppy.tsv: %.bam
	## TODO
	# $(DUPPY)

%.invy.tsv: %.bam
	## TODO
	# $(INVY)

%.jumpy.tsv: %.bam
	## TODO
	# $(JUMPY)



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
