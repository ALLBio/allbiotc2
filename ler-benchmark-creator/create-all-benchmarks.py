#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, division
from optparse import OptionParser, OptionGroup
import sys
import os
import subprocess
from itertools import product
from Bio import SeqIO

__author__ = "Tobias Marschall"

chromosomes = ['Chr%d'%i for i in range(1,6)]
insert_size_means = [500]
insert_size_stddevs = [15,50]
coverage = 30
sim_readlength = 100

print('='*100)
print('Downloading reference genome')
for chromosome in chromosomes:
	os.system('wget -O - ftp://ftp.ncbi.nlm.nih.gov/genbank/genomes/Eukaryotes/plants/Arabidopsis_thaliana/TAIR10/Primary_Assembly/assembled_chromosomes/FASTA/{0}.fa.gz| gunzip | sed -r "s|>.*|>{1}|g" > {1}.fasta'.format(chromosome.lower(), chromosome))
os.system('cat {0} > tair10.fasta'.format(' '.join(s+'.fasta' for s in chromosomes)))
print('Downloading LER variants (SDI file)')
os.system('wget http://mus.well.ox.ac.uk/19genomes/variants.SDI/ler_0.v7c.sdi')

print('='*100)
print('Converting LER variants to VCF')
os.system('./sdi-to-vcf.py -p -n LER ler_0.v7c.sdi tair10.fasta > ler_0.v7c.vcf')

print('='*100)
print('Creating reconstructed LER genome')
if not os.path.exists('ler-genome'):
	os.mkdir('ler-genome')
os.system('./genomesimulator.py ler_0.v7c.vcf tair10.fasta ler-genome')

print('='*100)
print('Simulating reads')
if not os.path.exists('ler-reads'):
	os.mkdir('ler-reads')
for insert_size_mean, insert_size_stddev in product(insert_size_means,insert_size_stddevs):
	output_filename = 'ler-reads/mean{0}-stddev{1}-cov{2}.sam.gz'.format(insert_size_mean, insert_size_stddev, coverage)
	zip_output = subprocess.Popen('gzip', stdin=subprocess.PIPE, stdout=open(output_filename,'w'))
	for chromosome in chromosomes:
		for allele in [1,2]:
			input_filename = 'ler-genome/LER.%s.%d.fasta'%(chromosome,allele)
			input_chromosome = list(SeqIO.parse(open(input_filename), "fasta"))
			assert len(input_chromosome) == 1
			length = len(input_chromosome[0].seq)
			#print(input_filename, 'has length', length, file=sys.stderr)
			read_pairs = coverage/2.0*length/(2*sim_readlength)
			print('Simulating %d read pairs from chromosome %s allele %d'%(read_pairs,chromosome,allele), file=sys.stderr)
			prefix = 'sim_%s_%d_'%(chromosome,allele)
			cmdline = 'simseq -1 %d -2 %d --error simseq-params/hiseq_mito_default_bwa_mapping_mq10_1.txt --error2 simseq-params/hiseq_mito_default_bwa_mapping_mq10_2.txt --insert_size %d --insert_stdev %d --read_number %d --read_prefix %s --reference %s --duplicate_probability 0.01 --out /dev/stdout'%(sim_readlength,sim_readlength,insert_size_mean,insert_size_stddev,read_pairs,prefix,input_filename)
			print(cmdline, file=sys.stderr)
			simreads = subprocess.Popen(cmdline.split(), stdout=zip_output.stdin)
			simreads.wait()
	zip_output.stdin.close()

print('='*100)
print('Creating FASTQ files')
for insert_size_mean, insert_size_stddev in product(insert_size_means,insert_size_stddevs):
	input_filename = 'ler-reads/mean{0}-stddev{1}-cov{2}.sam.gz'.format(insert_size_mean, insert_size_stddev, coverage)
	os.system('zcat ler-reads/mean{0}-stddev{1}-cov{2}.sam.gz | ./sam2fastq.py -z -u -s ler-reads/mean{0}-stddev{1}-cov{2}.1.fastq.gz ler-reads/mean{0}-stddev{1}-cov{2}.2.fastq.gz'.format(insert_size_mean, insert_size_stddev, coverage))
