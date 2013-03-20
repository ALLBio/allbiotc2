#!/usr/bin/make

## TODO Convert to actual commands
##In order to determine the insert size for the bam file, we use the bam2cfg.pl from breakdancer.
##
##These packages are needed for breakdancer:
##$ cpan
##$ install Statistics:Descriptive
##$ install Math::CDF
##$ install GD::Graph::histogram
##
##
##This is the log of command used for running pindel on bwa-mapped data:
##
##Output from bam2cfg:
##
##---------------------
##readgroup:NA    platform:illumina       map:ERR031544.bwa-0.7.2.sorted.bam      readlen:50.22   lib:NA  num:10001       lower:357.65    upper:444.94    mean:409.49     std:10.95       SWnormality:-69.73 exe:samtools view
##---------------------
##
##Contents of pindel.cfg:
##
##----------------------
##
##ERR031544.bwa-0.7.2.sorted.bam  409.49  ERR031544.bwa-0.7.2.sorted.bam
##
##----------------------
##allbio:~$  /virdir/Scratch/software/pindel/trunk/pindel -f /virdir/Scratch/data/reads_and_reference/reference/TAIR9_chr_all.fas -i /home/allbio/pindel_bwa/pindel.cfg -o Ler-bwa -I -T 16 
##
##
##These commands for the bt2-mapped data:
##
##Output from bam2cfg:
##---------------------
##readgroup:NA    platform:illumina       map:Ler-bt2.sort.bam    readlen:50.20   lib:NA  num:10001       lower:359.46    upper:444.92    mean:409.50     std:10.71       SWnormality:-65.83      exe:samtools view
##---------------------
##
##Contents of pindel.cfg:
##
##----------------------
##
##Ler-bt2.sort.bam        409.48  Ler-bt2.sort.bam
##
##----------------------
##
##allbio:~$  /virdir/Scratch/software/pindel/trunk/pindel -f /virdir/Scratch/data/reads_and_reference/reference/TAIR9_chr_all.fas -i /home/allbio/pindel_bt2/pindel.cfg -o Ler-bt2 -I -T 16 