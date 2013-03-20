#!/bin/bash

# Stop on error
set -e;

## Bowtie
#FOLDER='/virdir/Scratch/data/reads_and_reference/bt2_run';
#FILE='Ler-bt2.sort.bam';

## BWA
#FOLDER='/virdir/Backup/reads_and_reference/bwa-0.7.2';
#FILE='ERR031544.bwa-0.7.2.sorted.bam';

## Testing
FILE='sample.bam';
touch $FILE;

## Sample run & output
#allbio@cloud-KVM:~$ time breakdancer_deploy_1.3.5/bin/breakdancer-max ERR031544.sort.bam.breakdancer.cfg > ERR031544.sort.bam.output
#Max Kahan error: 0
#real    3m23.701s
#user    3m20.901s
#sys     0m1.796s

## Run makefile
make -n $FILE.bd.vcf;

