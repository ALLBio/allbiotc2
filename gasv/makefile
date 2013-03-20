#!/usr/bin/make

## TODO Convert to actual commands
##1)bt2
##
##command: >java -Xms512m -Xmx2048m -jar BAMToGASV.jar Ler-bt2.sort.bam 
##input_file: Ler-bt2.sort.bam 
##output_file(s): Ler-bt2.sort.bam.info, Ler-bt2.sort.bam.gasv.in, Ler-bt2.sort.bam_all.deletion, Ler-bt2.sort.bam_all.insertion, Ler-bt2.sort.bam_all.inversion, Ler-bt2.sort.bam_all.divergent, Ler-bt2.sort.bam_all.translocation
##
##command: >java -jar GASV.jar --batch Ler-bt2.sort.bam.gasv.in
##input_file: Ler-bt2.sort.bam.gasv.in
##output_file(s): Ler-bt2.sort.bam.gasv.in.clusters
##
##2)bwa-0.7.2
##
##command: >java -Xms512m -Xmx2048m -jar BAMToGASV.jar ERR031544.bwa-0.7.2.sorted.bam 
##input_file: ERR031544.bwa-0.7.2.sorted.bam
##output_file(s): ERR031544.bwa-0.7.2.sorted.bam.info, ERR031544.bwa-0.7.2.sorted.bam.gasv.in, ERR031544.bwa-0.7.2.sorted.bam_all.deletion, ERR031544.bwa-0.7.2.sorted.bam_all.insertion, ERR031544.bwa-0.7.2.sorted.bam_all.inversion, ERR031544.bwa-0.7.2.sorted.bam_all.divergent, ERR031544.bwa-0.7.2.sorted.bam_all.translocation
##
##command: >java -jar GASV.jar --batch ERR031544.bwa-0.7.2.sorted.bam.gasv.in
##input_file: ERR031544.bwa-0.7.2.sorted.bam.gasv.in
##output_file(s): ERR031544.bwa-0.7.2.sorted.bam.gasv.in.clusters
##
##
##
##* All output files are stored in /virdir/Backup/work/GASV directory
##**Problem occurred when tried to run the bam file in bwa_run2 directory

##GASV/GASVPro workflow
##http://code.google.com/p/gasv/
##Documentation in pdf in the package
##
##
##STEP 1
##classic:
##java -Xms512m -Xmx2048m -jar BAMToGASV.jar Example.bam
##or with options
##java -Xms512m -Xmx2048m -jar BAMToGASV.jar Example.bam -MAPPING_QUALITY 30 -CUTOFF_LMINLMAX SD=3
##or if multiple libraries:
##java -Xms512m -Xmx2048m -jar BAMToGASV.jar Example.bam -LIBRARY_SEPARATED all
##
##STEP 2
##java -jar GASV.jar --batch Example.bam.gasv.in
##
##STEP 3 run with GASVPro (2 scripts provided)
##GASVPro-HQ.sh
##GASVPro.sh
