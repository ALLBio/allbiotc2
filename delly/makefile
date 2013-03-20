#!/usr/bin/make

## I ran Delly on the Ler dataset from Bowtie2 using a 16 core virtual machine (ubuntu).  The following commands:
## 
## -    Deletions: ./delly
## •       Tandem duplications: ./duppy
## •       Inversions: ./invy
## •       Translocations: ./jumpy
## 
## cd ~/Desktop/delly_v0.0.9
## ./delly -p -g ~/Desktop/TAIR9-cleanheader.fa -b ~/Desktop/Delly-breakpoint-file.txt -o ~/Desktop/Delly.txt ~/Desktop/Ler-bt2.sort.bam
## 
## ./duppy -p -g ~/Desktop/TAIR9-cleanheader.fa -b ~/Desktop/Delly-duppy-breakpoint-file.txt -o ~/Desktop/Delly-duppy.txt ~/Desktop/Ler-bt2.sort.bam
## 
## ./invy -p -g ~/Desktop/TAIR9-cleanheader.fa -b ~/Desktop/Delly-invy-breakpoint-file.txt -o ~/Desktop/Delly-invy.txt ~/Desktop/Ler-bt2.sort.bam
## 
## ./jumpy -p -g ~/Desktop/TAIR9-cleanheader.fa -b ~/Desktop/Delly-jumpy-breakpoint-file.txt -o ~/Desktop/Delly-jumpy.txt ~/Desktop/Ler-bt2.sort.bam
## 
## It does not appear that these need to be run sequentially, so they should be able to be run in parallel.
## 
## Of note is that the reference fasta file had to be modified so as to reduce the headers to exclude any commenting past the first space in the header. Once this was done, the program ran relatively quickly.
## 
## Next,
## 
## grep "Deletion" bwa-Delly-deletions.txt > bwa-Delly-deletions-list.tab 
## 
## then,
## 
## perl delly-extract-convert.pl bwa-Delly-deletions-list.tab > Delly-bwa.vcf
## 
## 