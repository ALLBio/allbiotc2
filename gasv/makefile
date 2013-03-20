#!/usr/bin/make

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