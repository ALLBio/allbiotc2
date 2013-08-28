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

def is_ambiguous(dna_string):
	for c in dna_string:
		if len(iupac[c]) > 1:
			return True
	return False

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
	parser.add_option("-n", action="store", dest="sample_name", default='default',
			help='Name of sample.')
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
	print('#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t{0}'.format(options.sample_name))
	deletion_count = 0
	deletion30_count = 0
	insertion_count = 0
	insertion30_count = 0
	invalid_insertions = 0
	substitution_count = 0
	substitution30_count = 0
	invalid_substitutions = 0
	snp_count = 0
	invalid_snps = 0
	heterozyguous_snps = 0
	for line in open(sdi_filename):
		fields = line.split()
		assert len(fields) >= 5, 'Offending line: "%s"'%line
		chromosome, pos, length, ref_allele, alt_allele = fields[0], int(fields[1]), int(fields[2]), fields[3], fields[4]
		#if chromosome.upper().startswith('CHR'):
			#chromosome = chromosome[3:]
			#assert len(chromosome) > 0
		if ref_allele != '-':
			assert chromosome in ref
			assert ref[chromosome][pos-1:pos-1+len(ref_allele)] == ref_allele
		if (ref_allele == '-'):
			# INSERTION
			assert length > 0
			if is_ambiguous(alt_allele):
				invalid_insertions += 1
				continue
			ref_char = ref[chromosome][pos-1]
			print(chromosome,pos,'.',ref_char,ref_char+alt_allele,'.','PASS','SVTYPE=INS;SVLEN=%d'%length,'GT',format_genotype('1/1',options.phase), sep='\t')
			insertion_count += 1
			if length >= 30:
				insertion30_count += 1
		elif (alt_allele == '-'):
			# DELETION 
			assert length < 0
			ref_char = ref[chromosome][pos-2]
			print(chromosome,pos-1,'.',ref_char+ref_allele,ref_char,'.','PASS','SVTYPE=DEL;SVLEN=%d'%length,'GT',format_genotype('1/1',options.phase), sep='\t')
			deletion_count += 1
			if length <= -30:
				deletion30_count += 1
		elif (len(ref_allele) == 1) and (len(alt_allele) == 1):
			# SNP
			assert length == 0
			assert (ref_allele != '-') and (alt_allele != '-'), line
			if is_ambiguous(ref_allele):
				invalid_snps += 1
				continue
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
				heterozyguous_snps += 1
			else:
				assert False
			snp_count += 1
		else:
			# SUBSTITUTION
			if is_ambiguous(alt_allele):
				invalid_substitutions += 1
				continue
			ref_char = ref[chromosome][pos-2]
			print(chromosome,pos-1,'.',ref_char+ref_allele,ref_char+alt_allele,'.','PASS','SVTYPE=MIX;SVLEN=%d'%length,'GT',format_genotype('1/1',options.phase), sep='\t')
			substitution_count += 1
			if abs(length) >=30:
				substitution30_count += 1
	print('Written %d SNPs, out of which %d are heterozyguous.'%(snp_count, heterozyguous_snps), file=sys.stderr)
	print('Written %d deletions, out of which %d are >= 30bp.'%(deletion_count, deletion30_count), file=sys.stderr)
	print('Written %d insertions, out of which %d are >= 30bp.'%(insertion_count, insertion30_count), file=sys.stderr)
	print('Written %d non-SNP substitutions, out of which %d have an effective size >= 30bp.'%(substitution_count, substitution30_count), file=sys.stderr)
	print('Skipped %d invalid SNPs (heterozyguous with two non-reference bases or ambiguous reference).'%invalid_snps, file=sys.stderr)
	print('Skipped %d insertions where the ALT allele contained ambiguous IUPAC characters (might be heterozyguous sites).'%invalid_insertions, file=sys.stderr)
	print('Skipped %d substitutions where the ALT allele contained ambiguous IUPAC characters (might be heterozyguous sites).'%invalid_substitutions, file=sys.stderr)

if __name__ == '__main__':
	sys.exit(main())
