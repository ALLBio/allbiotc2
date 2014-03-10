#!/usr/bin/env python3
from __future__ import print_function
from optparse import OptionParser
import sys
import os
import math
import gzip
import datetime
from collections import defaultdict
from fasta import FastaReader

__author__ = "Tobias Marschall"

usage = """%prog [options] <calls.vcf> <reference.fasta.gz>

Reads VCF format and reference genome, replaces each deletion by its leftmost
equivalent deletion, and outputs resulting VCF to stdout."""

allowed_dna_chars = set(['A','C','G','T','N','a','c','g','t','n'])

def valid_dna_string(s):
	chars = set(c for c in s)
	return chars.issubset(allowed_dna_chars)

def leftify_deletion(ref, start, end):
	while (start > 0) and (ref[start-1] == ref[end-1]) and not (ref[start-1] in ['N','n']):
		start -= 1
		end -= 1
	return start

def rightify_deletion(ref, start, end):
	while (end < len(ref)) and (ref[start] == ref[end]) and not (ref[start] in ['N','n']):
		start += 1
		end += 1
	return start

def leftify_insertion(ref, pos, seq):
	"""Insertion: ref --> ref[:pos]+seq+ref[pos:], that is, pos gives the position
	AFTER the insertion breakpoint and seq is the inserted sequence. Return the
	new position and the new sequence to be inserted."""
	i = len(seq) - 1
	while (pos > 0) and (ref[pos-1] == seq[i]) and not (seq[i] in ['N','n']):
		pos -= 1
		i -= 1
		if i < 0:
			i = len(seq) - 1
	return pos, seq[i+1:] + seq[:i+1]

def rightify_insertion(ref, pos, seq):
	"""Insertion: ref --> ref[:pos]+seq+ref[pos:], that is, pos gives the position
	AFTER the insertion breakpoint and seq is the inserted sequence. Return the
	new position and the new sequence to be inserted."""
	i = 0
	while (pos < len(ref)) and (ref[pos] == seq[i]) and not (seq[i] in ['N','n']):
		pos += 1
		i += 1
		if i == len(seq):
			i = 0
	return pos, seq[i:] + seq[:i]

class Stats:
	def __init__(self):
		self.shiftedcounter = 0
		self.counter = 0
		self.totalshift = 0
	def add(self, shift):
		self.counter += 1
		if shift > 0:
			self.shiftedcounter += 1
			self.totalshift += shift
	def to_file(self, f, varname):
		print("------------------------ %s ------------------------"%varname.upper(), file=f)
		print("Overall number of %s: %d:" % (varname,self.counter), file=f)
		if self.counter > 0:
			print("Shifted %d %s" % (self.shiftedcounter,varname), file=f)
			if self.shiftedcounter > 0:
				print("Percentage of not sufficiently 'shifted' %s: %.2f" % (varname,float(self.shiftedcounter)*100.0/self.counter), file=f)
				print("Average shift for shifted %s in bp: %.2f" % (varname,float(self.totalshift)/self.shiftedcounter), file=f)
				print("Average overall shift (all %s) in bp: %.2f" % (varname,float(self.totalshift)/self.counter), file=f)

if __name__ == '__main__':
	parser = OptionParser(usage=usage)
	parser.add_option("--rightmost", action="store_true", dest="rightmost", default=False, help="Replace by rightmost (instead of leftmost) equivalent deletion.")
	parser.add_option("-H", action="store_true", dest="new_header", default=False, help="Replace header by a new one.")
	parser.add_option("-s", action="store_true", dest="suppress", default=False, help="Suppress VCF lines that couldn't be recognized as insertions or deletions")
	(options, args) = parser.parse_args()
	
	if (len(args) != 2):# or (os.isatty(0)):
		parser.print_help()
		sys.exit(1)
	
	vcf_filename = args[0]
#       construction site: would be helpful to open gzipped vcf directly
#		
	filesuffix = args[0].split('.')[-1]
#	if filesuffix == 'gz':
#		filebase = '.'.join(args[0].split('.')[:-2])
#		vcffile = gzip.open(args[0], 'rb')
#	elif filesuffix == 'vcf':
#		filebase = '.'.join(args[0].split('.')[:-1])
#		vcffile = open(args[0], 'r')

	filebase = '.'.join(args[0].split('.')[:-1])
#	vcffile = open(args[0], 'r')
	print(filebase, filesuffix, file=sys.stderr)

#	lines = vcffile.readlines()
#	print(lines, file=sys.stderr)
#	vcffile.close()

	leftfilename = filebase + '.shifted'
	statsfilename = filebase + '.stats'

	leftfile = open(leftfilename, "w")
	statsfile = open(statsfilename, "w")

	# Read reference sequence
	fasta_reader = FastaReader(args[1])
	reference = {}
	reference_order = []
	for s in fasta_reader:
		chromosome = s.name.split()[0]
		if chromosome[:3] == 'chr':
			chromosome = chromosome[3:]
		print('Loaded chromosome "{}"'.format(chromosome), file=sys.stderr)
		reference_order.append(chromosome)
		reference[chromosome] = s.sequence.upper()

	deletion_stats = Stats()
	insertion_stats = Stats()
	linenr = 0
	variant_count = 0
	other_variant_counter = 0
	if options.new_header:
		print('##fileformat=VCFv4.1')
		print('##fileDate=%s'%datetime.datetime.now().strftime('%Y%m%d'))
		print('##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">')
		for chromosome in reference_order:
			print('##contig=<ID=%s,length=%d>'%(chromosome,len(reference[chromosome])))
		print('##source=canonify-vcf.py')
	header_complete = False
	for line in (s.strip() for s in open(vcf_filename)):
		if (variant_count>0) and (variant_count % 50000 == 0):
			print("Touched %d variants: %d deletions, %d insertions and %d others." % (variant_count, deletion_stats.counter, insertion_stats.counter, other_variant_counter), file=sys.stderr)
		linenr += 1
		#print('Processing line', linenr, file=sys.stderr)
		if line.startswith('##'):
			if not options.new_header:
				print(line)
			continue
		elif line.startswith('#'):
			header = line.split()
			assert len(header) >= 8, 'Invalid header line: %s'%line
			if len(header) == 8:
				header = header + ['FORMAT']
			if len(header) == 9:
				header = header + ['default']
			if options.new_header:
				header = ['#CHROM','POS','ID','REF','ALT','QUAL','FILTER', 'INFO', 'FORMAT'] + header[9:]
			print('\t'.join(header))
			header_complete = True
			continue
		if not header_complete and options.new_header:
			print('#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tdefault')
			header_complete = True
		fields = line.split('\t', 10)
		#print('Line:', line, file=sys.stderr)
		#print('Fields:', fields, file=sys.stderr)
		assert len(fields) >= 8, 'Invalid line: %d'%linenr
		chrom = fields[0]
		if chrom.startswith('chr'):
			chrom = chrom[3:]
		variant_start = int(fields[1]) - 1
		variant_id = fields[2]
		variant_ref = fields[3]
		variant_alt = fields[4]
		quality = fields[5]
		filter_status = fields[6]
		info = fields[7]
		info_dict = dict(s.split('=') for s in info.split(';') if len(s.split('=')) == 2)
		format_field = fields[8] if len(fields) >= 9 else 'GT'
		genotype = fields[9] if len(fields) >= 10 else '1/.'
		if not chrom in reference:
			print('Cannot canonify line %d: unknown reference chromosome %s'%(linenr, chrom), file=sys.stderr)
			print(line)
			continue
		ref = reference[chrom]
		if (variant_ref in ['.','N']) and ('SVTYPE' in info_dict) and ('SVLEN' in info_dict):
			if info_dict['SVTYPE'] == 'INS':
				variant_ref = reference[chrom][variant_start]
			elif info_dict['SVTYPE'] == 'DEL':
				length = abs(int(info_dict['SVLEN']))
				variant_ref = reference[chrom][variant_start:variant_start+length+1]
		if ((variant_alt in ['.','N']) or (variant_alt == '<INS>')) and ('SVTYPE' in info_dict) and (info_dict['SVTYPE'] == 'INS') and ('SVLEN' in info_dict):
			length = abs(int(info_dict['SVLEN']))
			variant_alt = reference[chrom][variant_start] + ('N'*length)
		if ((variant_alt in ['.','N']) or (variant_alt == '<DEL>')) and ('SVTYPE' in info_dict) and (info_dict['SVTYPE'] == 'DEL') and ('SVLEN' in info_dict):
			variant_alt = reference[chrom][variant_start]
		if (not valid_dna_string(variant_ref)) or (not valid_dna_string(variant_alt)):
			print('Cannot canonify line %d: invalid/unknown variant type: %s --> %s'%(linenr, variant_ref, variant_alt), file=sys.stderr)
			if not options.suppress:
				print(line)
			other_variant_counter += 1
			continue
		if (len(variant_ref) > 1) and (len(variant_alt) == 1):
			# DELETION
			variant_end = variant_start + len(variant_ref)
			if (variant_end > len(ref)) or (ref[variant_start:variant_end] != variant_ref):
				print('Error: Reference mismatch in line %d: found %s but expected %s'%(linenr, variant_ref, ref[variant_start:variant_end]), file=sys.stderr)
				exit(1)
			if variant_alt != variant_ref[0]:
				print('Error: ALT not equal to first character of REF in line: %d (REF: %s, ALT: %s)'%(linenr, variant_ref,variant_alt), file=sys.stderr)
				exit(1)
			del_start = variant_start + 1
			del_end = variant_end
			if options.rightmost:
				new_del_start = rightify_deletion(ref, del_start, del_end)
			else:
				new_del_start = leftify_deletion(ref, del_start, del_end)
			shift = abs(del_start - new_del_start)
			deletion_stats.add(shift)
			if shift != 0:
				print('Moved deletion on chromosome %s from %d to %d'%(chrom,del_start+1,new_del_start+1), file=leftfile)
				variant_start = new_del_start - 1
				variant_ref = ref[variant_start:variant_start+len(variant_ref)]
				variant_alt = variant_ref[0]
				print('%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s%s'%(chrom,variant_start+1,variant_id,variant_ref,variant_alt,quality, filter_status, info, format_field, genotype, '\t'+fields[10] if len(fields)>10 else ''))
				#leftfile.write('%s\t%d\t%s\t%s\t%s\t%s'%(chrom,variant_start+1,variant_id,variant_ref,variant_alt,fields[5]))
			else:
				print('%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s%s'%(chrom,variant_start+1,variant_id,variant_ref,variant_alt,quality, filter_status, info, format_field, genotype, '\t'+fields[10] if len(fields)>10 else ''))
		elif (len(variant_ref) == 1) and (len(variant_alt) > 1):
			# INSERTION
			if (variant_start >= len(ref)) or (ref[variant_start] != variant_ref):
				print('Error: Reference mismatch in line %d: found %s but expected %s'%(linenr, variant_ref, ref[variant_start]), file=sys.stderr)
				exit(1)
			if variant_alt[0] != variant_ref:
				print('Error: REF not equal to first character of ALT in line: %d (REF: %s, ALT: %s)'%(linenr, variant_ref,variant_alt), file=sys.stderr)
				exit(1)
			# position directly AFTER breakpoint
			insertion_pos = variant_start + 1
			insertion_seq = variant_alt[1:]
			if options.rightmost:
				new_insertion_pos, new_insertion_seq = rightify_insertion(ref, insertion_pos, insertion_seq)
			else:
				new_insertion_pos, new_insertion_seq = leftify_insertion(ref, insertion_pos, insertion_seq)
			shift = abs(insertion_pos - new_insertion_pos)
			insertion_stats.add(shift)
			if shift != 0:
				print('Moved insertion on chromosome %s from %d to %d'%(chrom,insertion_pos,new_insertion_pos), file=leftfile)
				variant_start = new_insertion_pos - 1
				variant_ref = ref[variant_start]
				variant_alt = variant_ref + new_insertion_seq
				print('%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s%s'%(chrom,variant_start+1,variant_id,variant_ref,variant_alt,quality, filter_status, info, format_field, genotype, '\t'+fields[10] if len(fields)>10 else ''))
				#leftfile.write('%s\t%d\t%s\t%s\t%s\t%s'%(chrom,variant_start+1,variant_id,variant_ref,variant_alt,fields[5]))
			else:
				print('%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s%s'%(chrom,variant_start+1,variant_id,variant_ref,variant_alt,quality, filter_status, info, format_field, genotype, '\t'+fields[10] if len(fields)>10 else ''))
		else:
			print('Cannot canonify line %d: invalid/unknown variant type: %s --> %s'%(linenr, variant_ref, variant_alt), file=sys.stderr)
			if not options.suppress:
				print(line)
			other_variant_counter += 1
			continue
		variant_count += 1
	deletion_stats.to_file(statsfile, 'deletions')
	insertion_stats.to_file(statsfile, 'insertions')
