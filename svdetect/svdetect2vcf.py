#!/usr/bin/env python

import re
import argparse
import os

"""

COAMPLICON
DELETION
DUPLICATION
INSERTION
INS_FRAGMT
INV_COAMPLICON
INV_DUPLI
INVERSION
INV_FRAGMT
INV_INS_FRAGMT
INV_TRANSLOC
LARGE_DUPLI
SMALL_DUPLI
SV_type
TRANSLOC
UNDEFINED

chr_type        SV_type BAL_type        chromosome1     start1-end1     average_dist    chromosome2     start2-end2     nb_pairs        score_strand_filtering  score_order_filtering   score_insert_size_filtering     final_score     breakpoint1_start1-end1      breakpoint2_start2-end2

INTRA   SMALL_DUPLI     UNBAL   chr3    13590505-13591371       62      chr3    13590507-13591376       22222   99%     100%    100%    0.999   13591371-13591141       13590740-13590507
INTRA   SMALL_DUPLI     UNBAL   chr3    13591435-13592304       60      chr3    13591439-13592306       21852   99%     100%    100%    1.000   13592304-13592071       13591670-13591439
"""

class SV2VCF(object):
    regex = r"^(INTRA|INTER)\t(?P<type>[\w\_]+)\t(?P<balance>[\w]+)\t(?P<chromosome>[\w\d]+)\t(?P<start>[\d]+)-(?P<end>[\d]+)\t(?P<avg_dist>[\d]+)\t(?P<chromosome2>[\w\d]+)\t(?P<start2>[\d]+)-(?P<end2>[\d]+)"

    def __init__( self, svfile, reference ):
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
            chromosome =  self.reference.get( chromosome.replace('chr',''), None )
            return chromosome[ int(start )-1:int(stop)-1 ]
    

    def svtype( self, flag ):
        return {
            'D': 'DEL',
            'I': 'INS',
            'DELETION': 'DEL',
            'TRANSLOC': 'TRANS',
            'INSERTION': 'INS',
            'INVERSION': 'INV',
            'DUPLICATION': 'DUP',
            'SMALL_DUPLI': 'DUP_SMALL',
            'LARGE_DUPLI': 'DUP_LARGE',
            'INV_TRANSLOC': 'INV_TRANS',
            'COAMPLICON': 'COAMP',
        }.get( flag, '.' )

    def parseFile( self, sFile, *args, **kwargs ):
        """
            Returns vcf4.1 format, converted from svdetect output
        """
        with open(sFile,'r') as fd:
            # res = re.findall( r"^[\d]+\t(?P<type>[\w]+)[\w\d\" ]+\t", fd.read(), re.I | re.M )
            for res in re.finditer( self.regex, fd.read(), re.I | re.M ):                
                real_start = 'end'
                real_end = 'start2'

                # real_start = 'start'
                # real_end = 'end2'

                infodict = {
                    'id': '.',
                    'chromosome': res.group('chromosome').replace('chr',''),
                    'refbases': self.getrefbase( res.group('chromosome'), res.group('start'), res.group('start2')),
                    'start': int( res.group(real_start) ),
                    'end': int( res.group(real_end) ),
                    'quality': '.',
                    'filter': 'PASS',
                }
                altbases = '.'
                svtype = self.svtype( res.group('type') )
                svend = int( res.group('start2') )
                SVLEN=0

                
                if svtype == '.':
                    continue
                    # debug other SV types
#                   print res.groups()

                if svtype == 'DEL':
                    SVLEN = ( int(res.group(real_end)) - int(res.group(real_start)) ) * -1
                    SVLEN -= 1
                    altbases = infodict['refbases'][0:1]
                elif svtype == 'INS':
                    # in case of insertions
                    # with insertions, the svend is the start of the breakpoint
                    svend = res.group(real_start)
                    SVLEN = infodict[real_end] - infodict[real_start]
                    altbases = abs(SVLEN) * "N"

                infodict.update({
                    'altbases': altbases,
                })

                infofields = {
                    'program': 'svdetect',
                    'end': svend,
                    'supports': '.', #res.group('supports'),
                    'svlen': SVLEN,
                    'svtype': svtype,
                }
#                output = "%(chromosome)s\t%(start)s\t%(id)s\t%(refbases)s\t%(altbases)s\t%(quality)s\t%(filter)s" % infodict
#                output += "\tPROGRAM=%(program)s;END=%(end)s;DP=%(supports)s;SVLEN=%(svlen)s;SVTYPE=%(svtype)s" % infofields
                output = "%(chromosome)s\t%(start)s\t.\t.\t.\t%(quality)s\t%(filter)s" % infodict
                output += "\tPROGRAM=%(program)s;SVTYPE=%(svtype)s;SVLEN=%(svlen)s" % infofields

                print output


if __name__ == '__main__':
    """
        This script will print all output to commandline
    """
    parser = argparse.ArgumentParser()
    # args for first pair
    parser.add_argument('-f', '--file', dest='svfile', type=str,
            help='svdetect file')
    parser.add_argument('-r', '--reference', dest='reference', type=str,
            help='reference file')

    args = parser.parse_args()
    parser = SV2VCF( args.svfile, args.reference )
    parser.parseFile( args.svfile )


