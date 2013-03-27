#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division
from optparse import OptionParser
import sys
import os
from pysam import Samfile, AlignedRead
from Bio import SeqIO

__author__ = "Tobias Marschall"

usage = """%prog [options] <blat.psl> <ref.fasta> <contigs.fasta> <output.bam>

Reads a PSL file produced by blat and converts it to BAM."""

def read_fasta(filename):
	d = {}
	l = []
	for s in SeqIO.parse(open(filename), "fasta"):
		chromosome = s.name
		if chromosome[:3] == 'chr':
			chromosome = chromosome[3:]
		#print('Loaded chromosome "{}"'.format(chromosome), file=sys.stderr)
		d[chromosome] = s.seq.upper()
		l.append(chromosome)
	return d, l

def append_to_cigar(l, op_type, length):
	if len(l) == 0:
		l.append((op_type,length))
	elif l[-1][0] == op_type:
		l[-1] = (op_type, l[-1][1] + length)
	else:
		l.append((op_type,length))

def main():
	parser = OptionParser(usage=usage)
	#parser.add_option("-s", action="store_true", dest="sam_input", default=False,
					  #help="Input is in SAM format instead of BAM format")
	(options, args) = parser.parse_args()
	if len(args) != 4:
		parser.print_help()
		sys.exit(1)
	psl_filename = args[0]
	ref_filename = args[1]
	contigs_filename = args[2]
	bam_filename = args[3]
	liftover_dir = args[1]
	
	references, ref_chromosomes = read_fasta(ref_filename)
	refname_to_id = dict([(name,i) for i,name in enumerate(ref_chromosomes)])
	print('Read', len(ref_chromosomes), 'reference chromosomes:', ','.join(ref_chromosomes), file=sys.stderr)
	contigs, contig_names = read_fasta(contigs_filename)
	print('Read', len(contig_names), 'contigs.', file=sys.stderr)
	bam_header = {'HD': {'VN': '1.0'}, 'SQ': [dict([('LN', len(references[chromosome])), ('SN', chromosome)]) for chromosome in ref_chromosomes] }
	outfile = Samfile(bam_filename, 'wb', header=bam_header)

	line_nr = 0
	header_read = False
	for line in (s.strip() for s in open(psl_filename)):
		line_nr += 1
		if line.startswith('------'): 
			header_read = True
			continue
		if not header_read: continue
		fields = line.split()
		assert len(fields) == 21, 'Error reading PSL file, offending line: %d'%line_nr
		sizes = [int(x) for x in fields[18].strip(',').split(',')]
		contig_starts = [int(x) for x in fields[19].strip(',').split(',')]
		ref_starts = [int(x) for x in fields[20].strip(',').split(',')]
		assert 0 < len(sizes) == len(contig_starts) == len(ref_starts)
		strand = fields[8]
		contig_name = fields[9]
		ref_name = fields[13]
		assert strand in ['-','+']
		assert contig_name in contigs
		assert ref_name in references
		a = AlignedRead()
		a.qname = contig_name
		if strand == '+':
			a.seq = str(contigs[contig_name])
		else:
			a.seq = str(contigs[contig_name].reverse_complement())
		a.flag = (16 if strand == '+' else 0)
		a.rname = refname_to_id[ref_name]
		a.pos = ref_starts[0]
		a.mapq = 255
		qpos = contig_starts[0]
		refpos = ref_starts[0]
		cigar = []
		# soft-clipping at the start?
		if contig_starts[0] > 0:
			cigar.append((4,contig_starts[0]))
		longest_insertion = 0
		longest_deletion = 0
		total_matches = 0
		total_insertion = 0
		total_deletion = 0
		for length, contig_start, ref_start in zip(sizes, contig_starts, ref_starts):
			assert contig_start >= qpos
			assert ref_start >= refpos
			# insertion?
			if contig_start > qpos:
				insertion_length = contig_start - qpos
				longest_insertion = max(longest_insertion, insertion_length)
				total_insertion += insertion_length
				append_to_cigar(cigar, 1, insertion_length)
				qpos = contig_start
			# deletion?
			if ref_start > refpos:
				deletion_length = ref_start - refpos
				longest_deletion = max(longest_deletion, deletion_length)
				total_deletion += deletion_length
				append_to_cigar(cigar, 2, deletion_length)
				refpos = ref_start
			# strech of matches/mismatches
			append_to_cigar(cigar, 0, length)
			refpos += length
			qpos += length
			total_matches += length
		# soft-clipping at the end?
		if len(a.seq) > qpos:
			cigar.append((4,len(a.seq) - qpos))
		a.cigar = tuple(cigar)
		# only use contigs where longest deletion is <= 10000 bp
		if longest_deletion > 10000: continue
		# require at least 200 matching positions
		if total_matches < 200: continue
		# require the matching positions to make up at least 75 percent of the contig
		# (without counting parts of the contig that are insertions).
		if total_matches / (len(a.seq) - total_insertion) < 0.75: continue
		outfile.write(a)
	outfile.close()

if __name__ == '__main__':
	sys.exit(main())
