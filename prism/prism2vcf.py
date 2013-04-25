#!/usr/bin/env python
# -*- coding: utf-8 -*-

# prism2vcf.py
# 
import argparse
import csv

def parse_prism2vcf( prismfile, output_file ):
    oh = open(output_file, 'w')
    with open(prismfile, 'r') as ih:
        reader = csv.reader(ih, delimiter="\t")
        line = reader.next()
        for attrs in reader:
            chrom = attrs[0]
            pos = attrs[1]
            end = attrs[2]
            id = "."
            ref = "."
            var_type = attrs[4]
            if var_type == "INS":
                alt = attrs[21]
            else:
                alt = "."
            qual = "."
            filt = "PASS"
            var_len = int(end) - int(pos) + 1
            info = "PROGRAM=BWA,PRISM;SVTYPE=%s;SVLEN=%s" % (var_type, var_len)
            vcf_list = [chrom, pos, id, ref, alt, qual, filt, info]
            vcf_line = "\t".join(vcf_list) + "\n"
            oh.write(vcf_line)

    oh.close()

if __name__ == '__main__':
    """
        This script will print all output to commandline (/dev/stdout) or to -o
    """
    parser = argparse.ArgumentParser()
    # args for first pair
    parser.add_argument('-f', '--file', dest='prismfile', type=str,
            help='Prism input file')
    parser.add_argument('-o', '--outputvcf', dest='outputvcf', type=str,
            help='Output vcf to')

    args = parser.parse_args()
    parse_prism2vcf( args.prismfile, args.outputvcf )

