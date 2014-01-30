#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division
from optparse import OptionParser
import sys
import os
from string import maketrans
import subprocess
__author__ = "Tobias Marschall"

"""
Converts SAM format to FASTQ.
"""

usage = """Usage: %prog [options] <output.fastq>
or
       %prog -s [options] <output.1.fastq> <output.2.fastq>

Reads data in SAM format from stdin and writes FASTQ to given filename 
(use '-' for stdout). If option -s is given, two output files must be 
provided."""

def open_output(filename, zip_it):
	if filename == '-':
		out = sys.stdout
	else:
		out = open(filename, 'w')
	if zip_it:
		return subprocess.Popen('pigz', stdin=subprocess.PIPE, stdout=out).stdin
	else:
		return out

compl = maketrans('acgtACGT', 'tgcaTGCA')

def print_read(bits, name, seq, qual, output):
	# is "reverse" bit set? if so, we need to print the reverse sequence and phred string
	if bits & 16 == 0:
		print('@', name, sep='',file=output)
		print(seq.upper(),file=output)
		print('+',file=output)
		print(qual,file=output)
	else:
		print('@', name, sep='',file=output)
		print(seq[::-1].translate(compl).upper(),file=output)
		print('+',file=output)
		print(qual[::-1],file=output)

def main():
	parser = OptionParser(usage=usage)
	parser.add_option("-s", action="store_true", dest="split_pairs", default=False,
		help="Split pairs to different output files.")
	parser.add_option("-u", action="store_true", dest="skip_unclean", default=False,
		help="Skip sequences that contain characters not in {a,c,g,t,A,C,G,T}.")
	parser.add_option("-z", action="store_true", dest="gzip_output", default=False,
		help="Compress output in gzip format (invokes pigz).")
	(options, args) = parser.parse_args()
	if (options.split_pairs and (len(args)!=2)) or ((not options.split_pairs) and (len(args)!=1)) or (os.isatty(0)):
		parser.print_help()
		sys.exit(1)
	# create translation table that converts every character that is not in {a,c,g,t,A,C,G,T} to N
	nonACGT_to_N = ['N'] * 256
	for c in 'ACGTacgt':
		nonACGT_to_N[ord(c)] = c
	nonACGT_to_N = ''.join(nonACGT_to_N)

	if options.split_pairs:
		output0 = open_output(args[0], options.gzip_output)
		output1 = open_output(args[1], options.gzip_output)
		read0 = None
		for fields in (s.strip().split() for s in sys.stdin):
			bits = int(fields[1])
			name = fields[0]
			seq = fields[9]
			qual = fields[10]
			if read0 == None:
				assert (bits & 64 == 64) and (bits & 128 == 0)
				read0 = (bits, name, seq, qual)
			else:
				assert (bits & 64 == 0) and (bits & 128 == 128)
				bits0, name0, seq0, qual0 = read0
				assert name0 == name
				if options.skip_unclean:
					if (seq0.translate(nonACGT_to_N).find('N')>=0) or (seq.translate(nonACGT_to_N).find('N')>=0):
						read0 = None
						continue
				print_read(bits0,name0,seq0,qual0,output0)
				print_read(bits,name,seq,qual,output1)
				read0 = None
	else:
		output = open_output(args[0], options.gzip_output)
		for fields in (s.strip().split() for s in sys.stdin):
			bits = int(fields[1])
			name = fields[0]
			seq = fields[9]
			qual = fields[10]
			if options.skip_unclean and (seq.translate(nonACGT_to_N).find('N') >=0): continue
			print_read(bits,name,seq,qual,output)

if __name__ == '__main__':
	sys.exit(main())

