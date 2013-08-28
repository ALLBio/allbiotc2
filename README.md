# ALLBio testcase #2

This repository is used to store scripts written during the hackathon of ALLBio Testcase 2.
The aims of this project are:

* to provide a pipeline for Structural variation calling
* use this pipeline for benchmarking sv callers


More information about the project can be found at the following websites:

[ALLBio Bioinformatics](http://www.allbioinformatics.eu/), [Testcase#2](http://www.allbioinformatics.eu/doku.php?id=public:loadedtestcases:tc2), [Google site, members only!](https://sites.google.com/site/allbiotc2/)


## How to install


Grab a copy of this repository from GitHub to your home folder and store this in allbiotc2:

	cd ~
	git clone https://github.com/ALLBio/allbiotc2.git
	cd allbiotc2/
	make install
The `make install` command will do a system-wide install. This step requires `sudo` rights.


## Preprocessing reference VCF

If reference calls are provided in `SDI` format, the following procedure can be followed to convert from SDI to VCF.


	make -f ../scripts/Makefile \
	    REFERENCE_VCF=~/myworkdir/ref_all.complete.vcf \
	    SDI_FILE=~/myworkdir/ler_0.v7c.sdi \
	    preprocess

## Installing the software

The software for the pipeline is placed into one central location in the following setup:

	allbio@workbench:/virdir/Scratch/software$ tree -L 1
	.
	├── apache-ant-1.9.0
	├── bedtools-2.17.0
	├── bowtie2-2.1.0
	├── breakdancer
	├── bwa-0.7.4
	├── circos-0.63-4
	├── clever-1.1
	├── clever-sv
	├── CNVnator_v0.2.7
	├── cnv-seq
	├── delly_v0.0.9
	├── download
	├── dwac-seq0.7
	├── FastQC
	├── GapCloser1.12-r6
	├── gasv
	├── ggplot2
	├── inGAP_3_0_1
	├── mrsfast-2.6.0.4
	├── picard-tools-1.86
	├── pindel
	├── PRISM_1_1_6
	├── root
	├── samtools-0.1.18
	├── samtools-0.1.19
	├── sickle-master
	├── snappy-java-1.0.3-rc3.jar
	├── sratoolkit.2.3.1-ubuntu64
	├── suppdatafile
	├── SVDetect_r0.8b
	├── SVM2
	├── SVMerge
	├── svtoolkit
	└── tarballs


## Running the pipeline

Configuration can be done in the conf.mk and upon invocation of the pipeline by passing them via the commandline.

The most important and required variables are: 

* `PROGRAMS`: Path to the directory where the programs are installed  
* `REFERENCE_DIR`: Path to the reference
* `REFERENCE_VCF`: Full path to the VCF file with reference SV calls for benchmarking
* `FASTQ_EXTENSION`: Filename extentension of the FastQ files
* `PEA_MARK`: Filenaming of the left read of FastQ: sample-`PEA_MARK`.`FASTQ_EXTENSION`
* `PEB_MARK`: Filenaming of the right read of FastQ: sample-`PEB_MARK`.`FASTQ_EXTENSION`
* `*_THREADS`: Set the amount of cores to used by the programs.


Example invocation of the pipeline:

	THREADS=8

	make -f ../scripts/Makefile \
	    PROGRAMS=/virdir/Scratch/software\
	    REFERENCE_DIR=../input/reference_tair9 \
	    FASTQC_THREADS=$THREADS \
	    BWA_OPTION_THREADS=$THREADS \
	    PEA_MARK=.1 \
	    PEB_MARK=.2 \
	    FASTQ_EXTENSION=fastq \
	    REFERENCE_VCF=/virdir/Backup/reads_and_reference/vcf_reference/ref_all.complete.vcf 

## Example setup of pipeline directories

	allbio@workbench:/virdir/Backup/synthetic_run$ tree -L 1
	.
	├── input
	│   ├── reference_tair10
	│   │   ├── bowtie2
	│   │   ├── bwa
	│   │   ├── reference.fa
	│   │   ├── reference.fa.fai
	│   ├── sim-reads_1.fastq
	│   ├── sim-reads_2.fastq
	│   ├── sim-reads.409_10.1.fastq
	│   ├── sim-reads.409_10.2.fastq
	│   ├── sim-reads.511_10.1.fastq
	│   ├── sim-reads.511_10.2.fastq
	├── log
	├── run_integrationtest
	│   ├── bd.cfg
	│   ├── comparison.tex
	│   ├── run.sh
	│   ├── sim-read-511_10.1.fastq -> ../input/sim-reads.511_10.1.fastq
	│   ├── sim-read-511_10.1.filtersync.stats
	│   ├── sim-read-511_10.1.singles.fastq
	│   ├── sim-read-511_10.1.trimmed.fastq
	│   ├── sim-read-511_10.2.fastq -> ../input/sim-reads.511_10.2.fastq
	│   ├── sim-read-511_10.2.trimmed.fastq
	│   ├── sim-read-511_10.bam
	│   ├── sim-read-511_10.bam.bai
	│   ├── sim-read-511_10.bd.vcf
	│   ├── sim-read-511_10.breakdancer
	│   ├── sim-read-511_10.delly
	│   ├── sim-read-511_10.delly.vcf
	│   ├── sim-read-511_10.flagstat
	│   ├── sim-read-511_10.gasv
	│   ├── sim-read-511_10.gasv.vcf
	│   ├── sim-read-511_10.pindel
	│   ├── sim-read-511_10.pindel.vcf
	│   ├── sim-read-511_10.prism
	│   ├── sim-read-511_10.prism.vcf
	│   ├── sim-read-511_10.raw_fastqc
	│   ├── sim-read-511_10.sam
	│   ├── sim-read-511_10.trimmed_fastqc
	│   └── sim-read-511_10.unsort.bam
	└── scripts
	    ├── Makefile -> ~/allbiotc2/Makefile
	

