#!/usr/bin/make

## Paths to tools used
BREAKDANCER = /virdir/Scratch/software/breakdancer_deploy_1.3.5/
BREAKDANCER_MAX = $(BREAKDANCER)bin/breakdancer-max
BAM2CFG = $(BREAKDANCER)lib/breakdancer-max-unstable/bam2cfg.pl
BD2VCF = breakdancer2vcf.py

## Create configuration file for Breakdancer based on bam file
%.bd.cfg: %.bam
	perl $(BAM2CFG) $? > $@;

## Create the native tabular output file for breakdancer
%.bd.tsv: %.bd.cfg
	$(BREAKDANCER_MAX) $? > $@;

## Convert the native tabular file for breakdancer to variant call format file
%.bd.vcf: %.bd.tsv
	python $(BD2VCF) $?;

## Tool installation
install:
	## Not implemented; But here are some commented out stubs
	#sudo cpan Statistics::Descriptive;
	#sudo cpan GD::Graph::histogram;
	#sudo cpan Math::CDF;
	#git clone git://github.com/genome/breakdancer.git
	#cd breakdancer; git checkout v1.3.6;
	#wget http://breakdancer.sourceforge.net/morecpp.html;
