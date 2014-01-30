#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division
from optparse import OptionParser
import sys
import os
import re
import string
from collections import defaultdict
from Bio import SeqIO

__author__ = "Alex Schoenhuth and Tobias Marschall"

usage = """%prog [options] <variants.vcf> <reference.fasta(.gz)> <destination-folder>

Reads variations in VCF format, reads a whole reference genome, incorporates the variations
and writes one file per generated allele to 
<destination-folder>/<individual>.<chromosome>.<allelenr>.fasta"""

allowed_dna_chars = set(['A','C','G','T','N','a','c','g','t','n'])

def valid_dna_string(s):
	chars = set(c for c in s)
	return chars.issubset(allowed_dna_chars)

def add(variants_dict, chromosome, variant):
	variants_dict[chromosome].append(variant)

def make_chromosome(chr_out, liftover_out, log_out, chromosome, reference, variants):
	#print('make_chromosome:', chromosome, variants)
	print('  %d variants'%len(variants), file=sys.stderr)
	modrefchrom = [x for x in reference]
	print("Refchromlen:", len(modrefchrom), file=log_out) # at the beginning modrefchrom is refchrom
#	print(modrefchrom)
	delcount = inscount = mixcount = snpcount = mnpcount = invcount = transcount = 0
	inversions = []
	run = 0
	for vartype, left, right, seq in variants:
		#print(vartype, left, right, seq, file=sys.stderr) 
		if vartype == 'SNP':
			snpcount += 1
			if modrefchrom[left] != '':
				modrefchrom[left] = modrefchrom[left][:-1] + seq
		elif vartype == 'MNP':
			mnpcount += 1
			modrefchrom[right] = seq + modrefchrom[right]
			run += len(seq)
			for i in range(left, right):
				if modrefchrom[i] != '':
					modrefchrom[i] = modrefchrom[i][:-1]
					run -= 1
		elif vartype == 'INS':
			inscount += 1
			modrefchrom[left] = seq + modrefchrom[left]
			run += len(seq)

		elif vartype == 'DEL':
			delcount += 1
			for i in range(left, right):
				if modrefchrom[i] != '':
					modrefchrom[i] = modrefchrom[i][:-1] 
					run -= 1
		elif vartype == 'MIX':
			mixcount += 1
			modrefchrom[right] = seq + modrefchrom[right]
			run += len(seq)
			for i in range(left, right):
				if modrefchrom[i] != '':
					modrefchrom[i] = modrefchrom[i][:-1]
					run -= 1
		elif vartype == 'INV':
			invcount += 1
			inversions.append((left,right))
			print("INV!!")
		elif vartype == 'BND':
			transcount += 1
			delcount =-1 # since a translocation includes a deletion(in these cases)
			new_seq = ''.join(modrefchrom[left:right]) + modrefchrom[seq]
			modrefchrom[seq] = new_seq
			
		else:
			assert False
	for left, right in inversions:
		invseq = modrefchrom[left:right]
		invseq.reverse()
		modrefchrom[left:right] = invseq
	print("SNP:", snpcount, "MNP:", mnpcount, "MIX:", mixcount, "DEL:", delcount, "INS:", inscount, "INV:", invcount, "BND", transcount, file=log_out)
	print(run, file=log_out)
	# construct simchromstring
	simchrom = ''.join(modrefchrom)
	diff = len(simchrom) - len(modrefchrom) - run
	print("Len simchrom:", len(simchrom), "run:", run, "diff:", diff, file=log_out)
	if diff != 0:
		print("WARNING: diff not equal 0!", file=log_out)
	print(">chr%s" % (chromosome), file=chr_out)
	i = 0
	while i < len(simchrom):
		print(simchrom[i:i+50], file=chr_out)
		i += 50
	# write liftover file
	modind = 0
	numsame = 0
	diff = 0
	for ind, mer in enumerate(modrefchrom):        
		for x in mer:
			if diff == modind - ind:
				numsame += 1
			else: # diff != modind - ind
				print(numsame, diff, file=liftover_out)
				numsame = 1
				diff = modind - ind
			modind += 1
	if numsame > 0:
		print(numsame, diff, file=liftover_out)

if __name__ == '__main__':
	parser = OptionParser(usage=usage)
	#parser.add_option("-l", action="store", dest="liftover_file", default=None, 
						#help="Filename to store a liftover table at.")
	(options, args) = parser.parse_args()
	if len(args) != 3:
		parser.print_help()
		sys.exit(1)

	variants_filename = args[0]
	reference_filename = args[1]
	destination_folder = args[2]

	# read reference genome
	if reference_filename.endswith('.gz'):
		ref_in = subprocess.Popen(['gzip','-d'], stdin=open(reference_filename), stdout=subprocess.PIPE).stdout
	else:
		ref_in = open(reference_filename)
	reference = {}
	chromosomes = []
	for s in SeqIO.parse(ref_in, "fasta"):
		chromosome = s.name
		if chromosome[:3] == 'chr':
			chromosome = chromosome[3:]
		print('Loaded chromosome "{}"'.format(chromosome), file=sys.stderr)
		reference[chromosome] = s.seq.upper()
		chromosomes.append(chromosome)
	ref_in.close()
	
	# read variants
	# mapping (individual, chromosome, allelenr) to lists of tuples (vartype, coord1, coord2, seq)
	variants = defaultdict(list)
	#Separate dictionary for translocations since they require multiple lines (scatered) lines in a vcf file
	translocations = {}
	linenr = 0
	header = None
	individuals = None
	for line in (s.strip() for s in open(variants_filename)):
		linenr += 1
		if line.startswith('##'):
			continue
		if line.startswith('#'):
			header = line[1:].split('\t')
			assert len(header) >= 8
			individuals = header[9:]
			continue
		
		assert header != None
		fields = line.split('\t')
		assert len(fields) >= 8
		chrom = fields[0]
		variant_start = int(fields[1]) - 1
		variant_id = fields[2]
		variant_ref = fields[3]
		variant_alt = fields[4]
		variant_info = fields[7].split(';')[-1].split('=')[-1]
		variant_type = fields[7].split(';')[0].split('=')[-1]

		if not chrom in reference:
			print('Skipping variant for unknown reference "%s" in line %d'%(chrom,linenr), file=sys.stderr)
			continue
		ref = reference[chrom]
		if variant_alt == '<INV>':
			# INVERSION
			if not valid_dna_string(variant_ref):
				print('Warning: skipping invalid variant in line',linenr, file=sys.stderr)
				continue
			inversion_start = variant_start
			inversion_end = variant_start+len(variant_ref)
			for i,individual in enumerate(individuals):
				genotype = fields[9+i]
				add(variants, chrom, ('INV', inversion_start, inversion_end, ''))
		elif (re.match('\TRANS\d+',variant_info)) and (variant_type == 'BND'):
			# Translocations
			chrbreak = re.findall(r'\b\d+\b', variant_alt)
			if variant_info in translocations:
				#make sure the order of the breaks is right
				if translocations[variant_info]['break1']<int(max(chrbreak)):
					translocations[variant_info]['break2'] = int(max(chrbreak))-1
				else:
					translocations[variant_info]['break2'] = translocations[variant_info]['break1']
					translocations[variant_info]['break1'] = int(max(chrbreak))-1
					translocations[variant_info]['pos'] = variant_start
				add(variants, chrom, ('BND', translocations[variant_info]['break1'], translocations[variant_info]['break2'], translocations[variant_info]['pos']))
			else:
				translocations[variant_info] = {}
				translocations[variant_info]['break1'] = int(max(chrbreak))-1
				translocations[variant_info]['pos'] = variant_start
		elif (len(variant_ref) == 1) and (len(variant_alt) == 1):
			# SNP
			if not valid_dna_string(variant_ref) or not valid_dna_string(variant_alt):
				print('Warning: skipping invalid variant in line',linenr, file=sys.stderr)
				continue
			for i,individual in enumerate(individuals):
				genotype = fields[9+i]
				add(variants, chrom, ('SNP', variant_start, None, variant_alt))
		elif (len(variant_ref) > 1) and (len(variant_ref) == len(variant_alt)):
			# MNP
			if not valid_dna_string(variant_ref) or not valid_dna_string(variant_alt):
				print('Warning: skipping invalid variant in line',linenr, file=sys.stderr)
				continue
			while (len(variant_ref) > 0) and (len(variant_alt) > 0) and (variant_ref[0] == variant_alt[0]):
				variant_ref = variant_ref[1:]
				variant_alt = variant_alt[1:]
				variant_start += 1
			if len(variant_ref) == 0:
				continue
			for i,individual in enumerate(individuals):
				genotype = fields[9+i]
				add(variants, chrom, ('MNP', variant_start, variant_start+len(variant_ref), variant_alt))
		elif (len(variant_ref) > 1) and (len(variant_alt) == 1):
			# DELETION
			if not valid_dna_string(variant_ref) or not valid_dna_string(variant_alt):
				print('Warning: skipping invalid variant in line',linenr, file=sys.stderr)
				continue
			variant_end = variant_start + len(variant_ref)
			if variant_alt != variant_ref[0]:
				print('Error: ALT not equal to first character of REF in line', linenr, file=sys.stderr)
				exit(1)
			del_start = variant_start + 1
			del_end = variant_end
			for i,individual in enumerate(individuals):
				genotype = fields[9+i]
				add(variants, chrom, ('DEL', del_start, del_end, ''))
		elif (len(variant_ref) == 1) and (len(variant_alt) > 1):
			# INSERTION
			if not valid_dna_string(variant_ref) or not valid_dna_string(variant_alt):
				print('Warning: skipping invalid variant in line',linenr, file=sys.stderr)
				continue
			if variant_alt[0] != variant_ref:
				print('Error: REF not equal to first character of ALT in line', linenr, file=conflictfile)
				exit(1)
			# position directly BEFORE breakpoint
			insertion_pos = variant_start + 1
			insertion_seq = variant_alt[1:]
			for i,individual in enumerate(individuals):
				genotype = fields[9+i]
				add(variants, chrom, ('INS', insertion_pos, None, insertion_seq))
		
		else:
			# MIX
			if not valid_dna_string(variant_ref) or not valid_dna_string(variant_alt):
				print('Warning: skipping invalid variant in line',linenr, file=sys.stderr)
				continue
			while (len(variant_ref) > 0) and (len(variant_alt) > 0) and (variant_ref[0] == variant_alt[0]):
				variant_ref = variant_ref[1:]
				variant_alt = variant_alt[1:]
				variant_start += 1
			for i,individual in enumerate(individuals):
				genotype = fields[9+i]
				add(variants, chrom, ('MIX', variant_start, variant_start+len(variant_ref), variant_alt))
	print('Read', variants_filename, file=sys.stderr)
	# produce new alleles
	for chromosome in chromosomes:
		#sort variants dictionary to handle breakends before the deletions for translocations
		v = variants[chromosome]
		v.sort(key=lambda x: x[0])
		ref = reference[chromosome]
		print('Processing chromosome', chromosome, file=sys.stderr)
		chr_out = open('%schr%s.fasta'%(destination_folder,chromosome), 'w')
		liftover_out = open('%schr%s.liftover'%(destination_folder,chromosome), 'w')
		log_out = open('%schr%s.log'%(destination_folder,chromosome), 'w')
		make_chromosome(chr_out, liftover_out, log_out, chromosome, ref, v)
		chr_out.close()
		liftover_out.close()
		log_out.close()

