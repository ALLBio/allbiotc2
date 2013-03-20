#!/usr/bin/env python

import re
import argparse
import os
import vcf

"""
Takes an incomplete VCF, and tries to complement the ref and alt fields (not for all cases)
Information should be stored in the INFO fields
"""

class VCFLite2VCF(object):
    def __init__( self, pindelfile, reference ):
        self.readFasta( reference )
    
    def readFasta( self, sFile, *args, **kwargs ):
        """
            Reads reference sequence into dictionary item
            key is the chromosome
            value is the sequence in one long string without whitespace
        """
        self.reference = {}
        
        with open(sFile,'r') as fd:
            for name_raw, seq in self.read_fasta(fd):
#                 print name_raw
                name = name_raw.replace('>','').split(' ')[0]
#                 print name
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
            chromosome =  self.reference.get( chromosome, None )
            return chromosome[ int(start )-1:int(stop)-1 ]
    

    def svtype( self, sFlag ):
        return {
            'D': 'DEL',
            'I': 'INS',
        }.get( sFlag )

    def parseFile( self, sFile, *args, **kwargs ):
        """
        """
        vcf_reader = vcf.Reader( open( sFile, 'r' ) )
        vcf_writer = vcf.Writer( open('/tmp/out.vcf', 'w'), vcf_reader)
        for record in vcf_reader:
        	ALT = record.ALT
        	record.REF = self.getrefbase( record.CHROM, record.start, record.end )
        	record.ALT = [self.getrefbase( record.CHROM, record.start, record.end )]
        	if 'INS' in record.INFO['SVTYPE']:
	        	SVLEN = abs(int(record.INFO['SVLEN'][0]))
	        	SVseq = SVLEN * "N"
	        	record.ALT = [self.getrefbase( record.CHROM, record.start, record.end )+SVseq]
	        	print record
	        	print record.INFO

	        vcf_writer.write_record(record)

if __name__ == '__main__':
    """
        This script will print all output to commandline
    """
    parser = argparse.ArgumentParser()
    # args for first pair
    parser.add_argument('-f', '--file', dest='vcflite', type=str,
            help='Pindel file')
    parser.add_argument('-r', '--reference', dest='reference', type=str,
            help='reference file')

    args = parser.parse_args()
    parser = VCFLite2VCF( args.vcflite, args.reference )
    parser.parseFile( args.vcflite )


