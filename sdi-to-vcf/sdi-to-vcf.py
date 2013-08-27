#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, division
from optparse import OptionParser, OptionGroup
import sys
from Bio import SeqIO
import datetime
import random

__author__ = "Tobias Marschall"

usage = """%prog [options] <input.sdi> <reference.fasta>

Reads SDI format and a reference FASTA and outputs VCF format."""

iupac = {
	'A':set(['A']),
	'C':set(['C']),
	'G':set(['G']),
	'T':set(['T']),
	'R':set(['A','G']),
	'Y':set(['C','T']),
	'M':set(['A','C']),
	'K':set(['G','T']),
	'W':set(['A','T']),
	'S':set(['C','G']),
	'B':set(['C','G','T']),
	'D':set(['A','G','T']),
	'H':set(['A','C','T']),
	'V':set(['A','C','G']),
	'N':set(['A','C','G','T'])
}

def format_genotype(gt, randomly_phase):
	if randomly_phase:
		if gt == '0/0':
			return '0|0'
		elif gt == '1/0':
			return random.choice(['1|0','0|1'])
		elif gt == '1/1':
			return '1|1'
		else:
			assert False
	else:
		return gt

def main():
	parser = OptionParser(usage=usage)
	parser.add_option("-p", action="store_true", dest="phase", default=False,
			help='Randomly phase heterozyguous variants.')
	parser.add_option("-s", action="store", dest="seed", default=23, type=int,
			help='Random seed for phasing (default=23).')
	(options, args) = parser.parse_args()
	if (len(args) != 2):
		parser.print_help()
		sys.exit(1)
	sdi_filename = args[0]
	ref_filename = args[1]
	random.seed(options.seed)
	
	ref = dict((s.name, str(s.seq)) for s in SeqIO.parse(open(ref_filename), "fasta"))
	print('##fileformat=VCFv4.1')
	print('##fileDate=%s'%datetime.datetime.now().strftime('%Y%m%d'))
	print('##source=sdi-to-vcf.py')
	print('#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tdefault')
	substitution_count = 0
	invalid_snps = 0
	for line in open(sdi_filename):
		fields = line.split()
		assert len(fields) >= 5, 'Offending line: "%s"'%line
		chromosome, pos, length, ref_allele, alt_allele = fields[0], int(fields[1]), int(fields[2]), fields[3], fields[4]
		if chromosome.upper().startswith('CHR'):
			chromosome = chromosome[3:]
			assert len(chromosome) > 0
		if ref_allele != '-':
			assert chromosome in ref
			assert ref[chromosome][pos-1:pos-1+len(ref_allele)] == ref_allele
		if (ref_allele == '-'):
			# INSERTION
			assert length > 0
			ref_char = ref[chromosome][pos-1]
			print(chromosome,pos,'.',ref_char,ref_char+alt_allele,'.','PASS','SVTYPE=INS;SVLEN=%d'%length,'GT',format_genotype('1/1',options.phase), sep='\t')
		elif (alt_allele == '-'):
			# DELETION 
			assert length < 0
			ref_char = ref[chromosome][pos-2]
			print(chromosome,pos-1,'.',ref_char+ref_allele,ref_char,'.','PASS','SVTYPE=DEL;SVLEN=%d'%length,'GT',format_genotype('1/1',options.phase), sep='\t')
		elif (len(ref_allele) == 1) and (len(alt_allele) == 1):
			# SNP
			assert length == 0
			assert (ref_allele != '-') and (alt_allele != '-'), line
			if len(iupac[alt_allele]) == 1:
				# homozyguous SNP
				print(chromosome,pos,'.',ref_allele,alt_allele,'.','PASS','.','GT',format_genotype('1/1',options.phase), sep='\t')
			elif len(iupac[alt_allele]) == 2:
				# heterozyguous SNP
				if not ref_allele in iupac[alt_allele]:
					invalid_snps += 1
					continue
				s = set(iupac[alt_allele])
				s.remove(ref_allele)
				print(chromosome,pos,'.',ref_allele,list(s)[0],'.','PASS','.','GT',format_genotype('1/0',options.phase), sep='\t')
			else:
				assert False
		else:
			# SUBSTITUTION
			substitution_count += 1
			pass
	print('Skipped %d non-SNP substitutions.'%substitution_count, file=sys.stderr)
	print('Skipped %d invalid SNPs (heterozyguous with two non-reference bases).'%invalid_snps, file=sys.stderr)
		#print(length, len(ref_allele), len(alt_allele))
	#vcf_reader = vcf.Reader(open(vcf_filename))
	## Quick and dirty fix for that PyVCF cannot process Integer fields with multiple comma-separated values
	##vcf_reader = vcf.Reader(subprocess.Popen(['sed','/^#/ s|Integer|String|g',vcf_filename], stdout=subprocess.PIPE).stdout)
	##sample_indices = dict((x,i) for i,x in enumerate(vcf_reader.samples))
	#l = []
	#for record in vcf_reader:
		#if not 'SVLEN' in record.INFO: continue
		#if not 'SVTYPE' in record.INFO: continue
		##assert (record.CHROM != last_chrom) or (record.POS >= last_pos)
		#l.append((record.CHROM, record.POS, record.INFO['SVLEN'][0], record.INFO['SVTYPE'][0], record))
		#print(record.CHROM, record.POS, record.INFO['SVLEN'][0], record.INFO['SVTYPE'][0])
	#l.sort()

if __name__ == '__main__':
	sys.exit(main())
