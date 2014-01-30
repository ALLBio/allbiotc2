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

__author__ = "Simon van Leeuwen, based on genomesimulater.py by: Alex Schoenhuth and Tobias Marschall"

usage = """
usage:

%prog [options] <variants.vcf> <reference.fasta(.gz)> <destination-folder>

info:

This script introduces indels and translocations in a sequence, the variants need to be stored in VCF format.
Currently indels are supported, however, they need to be specified as a single line in the VCF file and not 
as two seperate breakends (SVTYPE=BND).

Example indel:

#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO							FORMAT	LER
1	822678	.	T	TAAA	.	PASS	PROGRAM=reference_annotation;SVTYPE=INS;SVLEN=91;	GT	1|1
1	823779	.	TTA	T	.	PASS	PROGRAM=reference_annotation;SVTYPE=DEL;SVLEN=1;	GT	1|1

Translocations need multiple lines in a vcf file, therefore a EVENT id (EVENT=TRANS0 in the info field, see example) 
needs to be present to connect the different lines. Lines describing a breakpoint (SVTYPE=BND) are assumed to be part 
of a translocation. Both inter and intra chromosomal events are supported.

Example translocation:

#CHROM	POS	ID	REF	ALT		QUAL	FILTER	INFO						FORMAT	LER
1	7908413	.	.	[1:7910389[	.	.	SVTYPE=DEL;END=7910389;SVLEN=-1975;EVENT=TRANS0	GT	1|1
1	7908413	.	.	[4:11878861[	.	.	SVTYPE=BND;EVENT=TRANS0				GT	1|1
1	7910389	.	.	]4:11880837]	.	.	SVTYPE=BND;EVENT=TRANS0				GT	1|1


"""
# extracts and returns chromosome and position from the REF or ALT field in the VCF file
def extractTXmate( alt ):
    try:
        return re.findall(r"([\d\w\_]+)\:([\d]+)", alt, re.I | re.M)[0]
    except:
        raise IndexError

# The end of a variant can be specified in different ways in the vcf file.
# This function try's all posebilities and returns the end position.
# input:	VCF record from the vcf library
# output:	End position of the variant 
def get_sv_end( rec ):
   	try:
		SVEND = rec.INFO['END']
		if type(SVEND) is list:
			SVEND = str(SVEND[0])
		return(SVEND)
	except:
		pass
	try:
		SVEND = rec.INFO['BPWINDOW'][1]
		return(SVEND)
	except:
		pass
	try:
		SVLEN = rec.INFO['SVLEN']
		if type(SVLEN) is list:
			SVLEN = int(SVLEN[0])
		SVEND = rec.POS+SVLEN
		return(SVEND)
	except:
		pass
	try:
		SVEND = rec.INFO['SVEND']
		if type(SVEND) is list:
			SVEND = str(SVEND[0])
		return(SVEND)
	except:
		return('unknown')
    
# Reconstructs the chromosome introducing the events from the vcf file.
# input:	variants: parsed variants for this chromosome (dictionary)
#		ref: reference sequence of the chromosome	
#		chr_out: ouput file to store the new sequence
# output:	New sequence containing the variants is written to the ouput file.	
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
			SVEND = get_sv_end(rec)
			seq = reference[rec.CHROM][rec.POS]
			variants[rec.CHROM][SVTYPE+str(countv)] = {}
			variants[rec.CHROM][SVTYPE+str(countv)]['type'] = SVTYPE
			variants[rec.CHROM][SVTYPE+str(countv)]['chr1'] = rec.CHROM
			variants[rec.CHROM][SVTYPE+str(countv)]['pos1'] = int(rec.POS)
			variants[rec.CHROM][SVTYPE+str(countv)]['pos2'] = int(SVEND)
			variants[rec.CHROM][SVTYPE+str(countv)]['seq'] = seq
			countv += 1

		elif SVTYPE == 'INS':
			#first try to get the end of the event
			SVEND = get_sv_end(rec)
			seq = rec.ALT
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
		print('Processing chromosome', c, file=sys.stderr)
		chr_out = open('%schr%s.fasta'%(destination_folder,c), 'w')
		make_chromosome(v,ref,chr_out)
	























