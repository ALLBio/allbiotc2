#!/usr/bin/env python

__copyright__ = """
Copyright (C) 2013 - Tim te Beek
Copyright (C) 2013 - Wai Yi Leung
Copyright (C) 2013 AllBio (see AUTHORS file)
"""

__desc__ = """Convert breakdancer output to pseudo .vcf file format."""
__created__ = "Mar 18, 2013"
__author__ = "tbeek"

import argparse
import csv
import os.path
import sys


def main(tsvfile, vcffile):
    '''
    :param tsvfile: filename of input file.tsv
    :type tsvfile: string
    :param vcffile: filename of output file.vcf
    :type vcffile: string
    '''
    with open(tsvfile) as reader:
        # Parse file
        dictreader = _parse_tsvfile(reader)
        print dictreader.fieldnames

        # Write out file
        _format_vcffile(dictreader, vcffile)

    # Quick output
    with open(vcffile) as reader:
        print reader.read(1000)


def _parse_tsvfile(readable):
    '''
    Read readable using csv.Sniffer and csv.DictReader
    :param readable: open file.tsv handle to read with csv.DictReader
    :type readable: file
    '''
    prev, curr = 0, 0
    while True:
        line = readable.readline()
        if not line.startswith('#'):
            # lets start from prev # line, without the hash sign
            readable.seek(prev + 1)
            break
        else:
            prev = curr
            curr = readable.tell()

    # Determine dialect
    curr = readable.tell()
    #dialect = csv.Sniffer().sniff(readable.read(3000))
    dialect = 'excel-tab'
    readable.seek(curr)

    # Read file
    dictreader = csv.DictReader(readable, dialect=dialect)
    return dictreader


_tsv_fields = ('Chr1', 'Pos1', 'Orientation1',
               'Chr2', 'Pos2', 'Orientation2',
               'Type', 'Size', 'Score',
               'num_Reads', 'num_Reads_lib',
               'ERR031544.sort.bam')
# 'Chr1': '1',
# 'Pos1': '269907',
# 'Orientation1': '39+39-',
# 'Chr2': '1',
# 'Pos2': '270919',
# 'Orientation2': '39+39-',
# 'Type': 'DEL',
# 'Size': '99',
# 'Score': '99',
# 'num_Reads': '38',
# 'num_Reads_lib': '/home/allbio/ERR031544.sort.bam|38',
# 'ERR031544.sort.bam': 'NA'

_vcf_fields = ('CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO')


def _format_vcffile(dictreader, vcffile):
    '''
    Create a pseudo .vcf file based on values read from DictReader instance.
    :param dictreader: DictReader instance to read data from
    :type dictreader: csv.DictRedaer
    :param vcffile: output file.vcf filename
    :type vcffile: string
    '''
    with open(vcffile, mode='w') as writer:
        writer.write('#{}\n'.format('\t'.join(_vcf_fields)))
        output_vcf = []
        for line in dictreader:
            CHROM = line['Chr1']
            # TODO Figure out whether we have zero or one based positioning
            POS = int(line['Pos1'])
            SVEND = int(line['Pos2'])
            INFO = 'PROGRAM=breakdancer;SVTYPE={};SVLEN={}'.format(line['Type'],
                                                                   0 - int(line['Size']))
            if line['Type'] not in ['CTX']:
                INFO += ";SVEND={}".format(SVEND)

            # Create record
            output_vcf.append([CHROM, POS, '.', '.', '.', '.', 'PASS', INFO])

        # Sort all results
        output_vcf.sort()
        output = "\n".join(["\t".join(map(str,vcf_row)) for vcf_row in output_vcf])
        # Write record
        writer.write(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--breakdancertsv', dest='breakdancertsv', type=str,
            help='Breakdancer TSV outputfile')
    parser.add_argument('-o', '--outputvcf', dest='outputvcf', type=str,
            help='Output vcf to')

    args = parser.parse_args()
    main(args.breakdancertsv, args.outputvcf)
