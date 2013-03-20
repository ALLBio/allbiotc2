#!/usr/bin/env perl

my $filename=$ARGV[0];

open(FASTA, $filename) || die "failed $filename";

while(<FASTA>) {
	chomp;
	if (m/>Chr(\d);range=(\d+)\.\.(\d+)/ && $flag == 0) {
		$chrom = $1;
		$pos = $2;
		$id = ".";
	 	$qual = ".";
		$filter = "PASS";
		$info = "IMPRECISE;PROGRAM=reference_annotation;";
		$ref = '';
		$alt = '.';
		$len = '';
		$flag = 1;
	}
	elsif ((m/>Chr(\d);range=(\d+)\.\.(\d+)/ || eof) && $flag == 1) {
		if (eof) { $sequence .= $_; }
		$ref = $sequence;
		$len = length($sequence);	
		$info .= "SVTYPE=DEL;SVLEN=$len";
		print "$chrom\t$pos\t$id\t$ref\t$alt\t$qual\t$filter\t$info\n";
		$chrom = $1;
                $pos = $2;
                $id = ".";
                $qual = ".";
                $filter = "PASS";
                $info = "IMPRECISE;PROGRAM=reference_annotation;";
                $ref = '';
                $alt = '.';
                $len = '';
		$ref = '';	
		$sequence = '';
	}
	else {
		$sequence .= $_;
	}	
}	

