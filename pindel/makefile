#!/usr/bin/make

## Paths to tools used
BREAKDANCER = /virdir/Scratch/software/breakdancer_deploy_1.3.5/
BAM2CFG = $(BREAKDANCER)lib/breakdancer-max-unstable/bam2cfg.pl
PINDEL = /virdir/Scratch/software/pindel/trunk/pindel

##In order to determine the insert size for the bam file, we use the bam2cfg.pl from breakdancer.
%.pindel.cfg: %.bam
	perl $(BAM2CFG) $? > $*.bd.cfg;
	## TODO extract mean from $*.bd.cfg and store it in $@;
	##readgroup:NA    platform:illumina       map:ERR031544.bwa-0.7.2.sorted.bam      readlen:50.22   lib:NA  num:10001       lower:357.65    upper:444.94    mean:409.49     std:10.95       SWnormality:-69.73 exe:samtools view
	##ERR031544.bwa-0.7.2.sorted.bam  409.49  ERR031544.bwa-0.7.2.sorted.bam
	#python -c 'print open("$*.bd.cfg").read().split()[8].split(":")[1]' >> $@;

## Create the native tabular output file for pindel
%.pindel.tsv: %.pindel.cfg
	## TODO Ensure the $(REFERENCE) variable from the parent folder makefile is available here
	$(PINDEL) -f $(REFERENCE) -i $? -o $@ -I -T 4

## Convert the native tabular file for breakdancer to variant call format file
%.bd.vcf: %.bd.tsv
	## TODO Add the actual conversion script

## Tool installation
install:
	## Not implemented; But here are some commented out stubs
	#sudo cpan Statistics::Descriptive;
	#sudo cpan GD::Graph::histogram;
	#sudo cpan Math::CDF;
	#git clone git://github.com/genome/breakdancer.git
	#cd breakdancer; git checkout v1.3.6;
	#wget http://breakdancer.sourceforge.net/morecpp.html;
