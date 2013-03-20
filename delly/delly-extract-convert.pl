#!/usr/bin/perl
# modify delly output
# perl delly-extract-convert.pl delly-duplication.txt > output.vcf
use strict;
use warnings;

open (DELLY, "<$ARGV[0]") or die "Can not open DELLY output file : $!\n";
#open (OUT, ">Delly-bt2.vcf") or die " Can not open new DELLY vcf file: $!\n";

while (<DELLY>) {
	my @cols = split(/\t/);
	print  "$cols[0]\t$cols[1]\t\.\t\.\t\.\t\.\tPASS\tDELLY=BWA;SVTYPE=DEL;SVLEN=$cols[3]\n";
		
}


#close OUT;
close DELLY;
