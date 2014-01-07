#!/usr/bin/env python
# -*- coding: utf-8 -*-

# vcflite2vcf.py
# 
__doc__ = """
Takes an incomplete VCF, and tries to complement the ref and alt fields (not for all cases)
Information should be stored in the INFO fields
"""
__author__ = "Wai Yi Leung"
__contact__ = "w dot y dot leung apple lumc dot nl"
# (c) 2013 by Wai Yi Leung [LUMC - SASC]

import re
import argparse
import os
import vcf

class VCFLite2VCF(object):
    def __init__( self, reference, outputfile=None ):
        self.readFasta( reference )
        self.vcfoutput = '/tmp/out.vcf'
        if outputfile:
            self.vcfoutput = outputfile
        print self.vcfoutput
    
    def readFasta( self, sFile, *args, **kwargs ):
        """
            Reads reference sequence into dictionary item
            key is the chromosome
            value is the sequence in one long string without whitespace
        """
        self.reference = {}
        
        with open(sFile,'r') as fd:
            for name_raw, seq in self.read_fasta(fd):
                name = name_raw.replace('>','').split(' ')[0]
                self.reference[ name ] = seq

    #http://stackoverflow.com/questions/7654971/parsing-a-fasta-file-using-a-generator-python
    def read_fasta(self, fp):
        name, seq = None, []
        for line in fp:
            line = line.rstrip()
            if line.startswith(">"):
                if name: yield (name, ''.join(seq))
                name, seq = line, []
            else:
                seq.append(line)
        if name: yield (name, ''.join(seq))

    def getrefbase( self, chromosome, start, stop ):
        # expect coordinates in vcf file to be 1 indexed
        chromosome =  self.reference.get( chromosome, None )
        return chromosome[ int(start )-1:int(stop)-1 ]

    def parseFile( self, sFile, *args, **kwargs ):
        """
            Parse the vcflite file with PyVCF (0.6.3) 
            pip install git+git://github.com/jamescasbon/PyVCF.git@6280a655b4#egg=PyVCF
        """
        vcf_reader = vcf.Reader( open( sFile, 'r' ) )
        vcf_writer = vcf.Writer( open( self.vcfoutput, 'w'), vcf_reader)
        for record in vcf_reader:
            if ('SVTYPE' in record.INFO) and ('SVLEN' in record.INFO):
                SVLEN = abs(int(record.INFO['SVLEN']))
                if 'INS' in record.INFO['SVTYPE']:
                    SVseq = SVLEN * "N"
                    record.REF = self.getrefbase( record.CHROM, record.start, record.start + 1 )
                    record.ALT = [self.getrefbase( record.CHROM, record.start, record.end )+SVseq]
                elif 'DEL' in record.INFO['SVTYPE']:
                    record.REF = self.getrefbase( record.CHROM, record.start, record.start + SVLEN + 1)
                    record.ALT = [self.getrefbase( record.CHROM, record.start, record.start+1 )]
            vcf_writer.write_record(record)

if __name__ == '__main__':
    """
        This script will print all output to commandline (/dev/stdout) or to -o
    """
    parser = argparse.ArgumentParser()
    # args for first pair
    parser.add_argument('-f', '--file', dest='vcflite', type=str,
            help='VCF lite file')
    parser.add_argument('-o', '--outputvcf', dest='outputvcf', type=str,
            help='Output vcf to')
    parser.add_argument('-r', '--reference', dest='reference', type=str,
            help='reference file')

    args = parser.parse_args()
    parser = VCFLite2VCF( args.reference, args.outputvcf )
    parser.parseFile( args.vcflite )


