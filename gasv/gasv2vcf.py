#!/usr/bin/env python

__copyright__ = """
Copyright (C) 2013 AllBio (see AUTHORS file)
"""

__desc__ = """Convert GASV output to pseudo .vcf file format."""
__created__ = "Mar 18, 2013"
__author__ = "Xenofon Evangelopoulos"

###    USAGE:
###        python gasv2vcf.py [variants_file] [output_file] [BWA/BT2]
###

import csv
import sys

variants_file = sys.argv[1]
output_file = sys.argv[2]
prog = "%s,GASV" % sys.argv[3]

oh = open(output_file, 'w')
with open(variants_file, 'r') as ih:
    reader = csv.reader(ih, delimiter="\t")
    line = reader.next()
    for attrs in reader:
        chrom = attrs[1]
        pos1 = attrs[2]
        pos = pos1.split(',')[0]
        end1 = attrs[4]
        end =end1.split(',')[0]
        id = "."
        ref = "."
        vt = attrs[7]
        if vt == "D":
            var_type = "DEL"
        elif vt == "I":
            var_type = "INV"
        elif vt == "IR":
            var_type = "INV"
        elif vt == "I+":
            var_type = "INV"
        elif vt == "I-":
            var_type = "INV"
        elif vt == "V":
            var_type = "DIV"
        elif vt == "T":
            var_type = "TRN"
        elif vt in ['TR', 'TR+', 'TR-', 'TR+1', 'TR-1', 'TR+2', 'TR-2',]:
            var_type = "TRN"
        elif vt in ['TN', 'TN+', 'TN-', 'TN+1', 'TN-1', 'TN+2', 'TN-2',]:
            var_type = "TRN"
        else:
            var_type = "UNKNOWN"
        qual = "."
        alt = "."
        filt = "PASS"
        var_len = int(end) - int(pos)
        info = "PROGRAM=%s;SVTYPE=%s;SVLEN=%s" % (prog, var_type, var_len)
        vcf_list = [chrom, pos, id, ref, alt, qual, filt, info]
        vcf_line = "\t".join(vcf_list) + "\n"
        oh.write(vcf_line)

oh.close()
