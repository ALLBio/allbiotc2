#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division
from optparse import OptionParser
import sys
import os
import re
import string
import collections
from Bio import SeqIO
import vcf

usage = """%prog [options] <variants.vcf> <reference.fasta(.gz)> <destination-folder>"""

def extractTXmate( alt ):
    try:
        return re.findall(r"([\d\w\_]+)\:([\d]+)", alt, re.I | re.M)[0]
    except:
        raise IndexError

def make_chromosome(variants,ref,chr_out):
	modrefchrom = [x for x in ref]
	for v in variants.keys():
		svtype = variants[v]['type']
		pos1 = variants[v]['pos1']
		pos2 = variants[v]['pos2']
		seq = str(variants[v]['seq'])
		if svtype == 'INS':
			
			modrefchrom[pos1] = seq + modrefchrom[pos1]

		elif svtype == 'DEL':
			for i in range(pos1, pos2):
				if modrefchrom[i] != '':
					modrefchrom[i] = modrefchrom[i][:-1] 
	simchrom = ''.join(modrefchrom)
	print(">chr%s" % (chromosome), file=chr_out)
	i = 0
	while i < len(simchrom):
		print(simchrom[i:i+50], file=chr_out)
		i += 50

if __name__ == '__main__':
	parser = OptionParser(usage=usage)
	#parser.add_option("-l", action="store", dest="liftover_file", default=None, 
						#help="Filename to store a liftover table at.")
	(options, args) = parser.parse_args()
	if len(args) != 3:
		parser.print_help()
		sys.exit(1)

	vcf_filename = args[0]
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
	## insertions (part of a translocation)
	# <type> <chr1> <pos1> <pos2> <seq>
	## Deletion
	# <type> <chr1> <pos1> <pos2> <seq>
	variants = {}
	#create empty dictionary for every chromosome
	for c in chromosomes:
		variants[c]= {}
	
	vcf_reader = vcf.Reader(open(vcf_filename, 'r'))
        seen = []
	countv = 0
        for rec in vcf_reader:
		#Go to the next line if svtype field is not present (snp's)
		try:
			SVTYPE = rec.INFO['SVTYPE']
		except:
			continue
	    	if type(SVTYPE) is list:
			SVTYPE = str(SVTYPE[0])
		if SVTYPE == 'BND':
			event = rec.INFO['EVENT'][0] 
			if event in seen:
				#create an insertion for the translocated segment, also store the inserted sequence
				chr2, pos2 = extractTXmate( str(rec.ALT.pop()) )
				pos1 = variants[rec.CHROM][event]['pos1']
				pos3 = variants[rec.CHROM][event]['pos2']
				seq = reference[rec.CHROM][int(pos1):int(rec.POS)]
				variants[chr2][event] = {}
				variants[chr2][event]['type'] = 'INS'
				variants[chr2][event]['chr1'] = chr2
				variants[chr2][event]['pos1'] = int(pos3)
				variants[chr2][event]['pos2'] = int(pos2)
				variants[chr2][event]['seq'] = seq
				#delete first encounter, all the information is now in the insertion on the 'new' chromosome (only for inter chrom events)
				if rec.CHROM != chr2:
					del variants[rec.CHROM][event]
			else:
				#store information untill the next line of this event is encountered
				variants[rec.CHROM][event] = {}
				chr1, pos2 = extractTXmate( str(rec.ALT.pop()) )
				variants[rec.CHROM][event]['type'] = 'trans'
				variants[rec.CHROM][event]['chr1'] = rec.CHROM
				variants[rec.CHROM][event]['pos1'] = int(rec.POS)
				variants[rec.CHROM][event]['pos2'] = int(pos2)
				seen.append(event)

		elif SVTYPE == 'DEL':
			#first try to get the end of the event
			try:
				SVEND = rec.INFO['END']
				if type(SVEND) is list:
					SVEND = str(SVEND[0])
			except:
				pass
			try:
				SVEND = rec.INFO['BPWINDOW'][1]
			except:
				pass
			try:
				SVEND = rec.POS+int(rec.INFO['SVLEN'])
			except:
				pass
			try:
		   		SVEND = rec.INFO['SVEND']
				if type(SVEND) is list:
					SVEND = str(SVEND[0])
			except:
				pass#SVEND = rec.POS+int(rec.INFO['SVLEN'][0])

			seq = reference[rec.CHROM][rec.POS]
			variants[rec.CHROM][SVTYPE+str(countv)] = {}
			variants[rec.CHROM][SVTYPE+str(countv)]['type'] = SVTYPE
			variants[rec.CHROM][SVTYPE+str(countv)]['chr1'] = rec.CHROM
			variants[rec.CHROM][SVTYPE+str(countv)]['pos1'] = int(rec.POS)
			variants[rec.CHROM][SVTYPE+str(countv)]['pos2'] = int(SVEND)
			variants[rec.CHROM][SVTYPE+str(countv)]['seq'] = seq
			countv += 1
	#print(variants)
	for c in chromosomes:
		ref = reference[c]
		v = variants[c]
		print(v)
		print('Processing chromosome', c, file=sys.stderr)
		print('Processing chromosome', c)
		chr_out = open('%schr%s.fasta'%(destination_folder,c), 'w')
		make_chromosome(v,ref,chr_out)
	























