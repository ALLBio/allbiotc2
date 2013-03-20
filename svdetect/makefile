#!/usr/bin/make

## TODO Convert to actual commands
##SVDetect works with a BAM file and a FASTA reference file
##We need to set up a text file containing the list of chromosomes and their size in tab-delimited file e.g.:
##1 1 30427671
##2 2 19698289
##3 3 23459830
##4 4 18585056
##5 5 26975502
##6 mitochondria 366924
##7 chloroplast 154478
##
##Then you need to run 3 steps:
##
##a) BAM_preprocessingPairs.pl Ler-bt2.bam  # creates Let-bt2.ab.bam, takes a few minutes (12 minutes)
##manually modify config file to take into account insert size (mu=411) and SD (sigma=73) (follow recommandations of manual)
##Window size for balanced translocation = 2*mu+2*(2*sigma)^1/2 = 846
##Step = 1/4 of Window size = 211
##
##b) SVDetect linking filtering -conf ler.sv.conf 
### Making the fragments library...
##takes several hours (8 !!)
##automatically using 5 processors (1 per chromosome)
##memory usage, less than 10Gb
##
##c) SVDetect links2SV -conf ler.sv.conf
###extracting SV very fast step, generates final file: Ler-bt2.ab.bam.all.links.filtered.sv.txt
##
##chr_type SV_type BAL_type chromosome1 start1-end1 average_dist chromosome2 start2-end2 nb_pairs score_strand_filtering score_order_filtering score_insert_size_filtering final_score breakpoint1_start1-end1 breakpoint2_
##start2-end2
##INTRA SMALL_DUPLI UNBAL chr3 13590505-13591371 62 chr3 13590507-13591376 22222 99% 100% 100%
## 0.999 13591371-13591141 13590740-13590507
##INTRA SMALL_DUPLI UNBAL chr3 13591435-13592304 60 chr3 13591439-13592306 21852 99% 100% 100%
## 1.000 13592304-13592071 13591670-13591439
## 




##SVDetect workflow
##http://svdetect.sourceforge.net/Site/Home.html
##http://svdetect.sourceforge.net/Site/Manual.html
##
#####This is a example of script for using SVDetect
#### DATA:
#### Illumina 50bp sequencing reads in mate-pair
#### Organism : Human
#### Sample data: neuroblastoma cell lines
#### Reference data: normal cell lines
##
###Generation and filtering of links from the sample data
##SVDetect linking filtering -conf sample.sv.conf
##
###Generation and filtering of links from the reference data
##SVDetect linking filtering -conf reference.sv.conf
##
###Comparison of links between the two datasets
##SVDetect links2compare -conf sample.sv.conf
##
###Calculation of depth-of-coverage log-ratios
##SVDetect cnv ratio2circos ratio2bedgraph -conf sample.cnv.conf
##
###Visualization of filtered links and copy-number profiles in Circos
##circos -conf circos/sample.circos.conf
##
##
### comments:
##Files needed (must modify conf file): 
##mates_file=sample_ab_mates.sam
##mates_file=reference_ab_mates.sam
##cmap_file=hs18.len
##
##Comparison is not mandatory, but it strengthen the results. 
##We can get already predictions with a single genome.
##
##Plus updated config files:
##sample.sv.conf
##reference.sv.conf
##circos/sample.circos.conf
##
##Requires a script BAM_preprocessingPairs.pl
##Rather slow with test data set: 
##problems with circos.
