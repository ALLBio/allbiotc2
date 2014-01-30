#!/bin/bash

if [ $# -ne 2 ] ; then 
	echo "usage: $0 <mean> <stddev>"
	exit 1
fi
readlength=100
insert_mean=$1 # 511.345
insert_stddev=$2 # 10.3838
dataset="${insert_mean}_${insert_stddev}"
coverage=30
genomelength=119667750
let totalreadlength=2*readlength
let readcount=coverage*genomelength/totalreadlength
# echo readcount: ${readcount}
./simseq -1 ${readlength} -2 ${readlength} --error hiseq_mito_default_bwa_mapping_mq10_1.txt --error2 hiseq_mito_default_bwa_mapping_mq10_2.txt --insert_size ${insert_mean} --insert_stdev ${insert_stddev} --read_number ${readcount} --read_prefix sim_ --reference ../inter_chr_analysis/data/genome/inter_genome.fasta --duplicate_probability 0.01 --out /dev/stdout | pigz > sim-reads.${dataset}.sam.gz
zcat sim-reads.${dataset}.sam.gz | python ./sam2fastq.py -s sim-reads_${dataset}.1.fastq sim-reads_${dataset}.2.fastq
