#!/usr/bin/env perl

my $filename = $ARGV[0];
#my $reference = $ARGV[1];
#open(FASTA, $reference) || die "failed reference"; 
#my $flag =0;

#while(<FASTA>) {
#	chomp;
#	if ($_ =~ m/>(.*)/ && $flag == 0) { 
#		$chrom{$header}=$sequence;
#		$header = $1;
#		$flag = 1;
#	}
#	else  {
#		$flag = 0;
#		$sequence .= $_;
#	}
#}

#$/='\n';
open(READ, $filename) || die "failed";
while(<READ>) {
	chomp;
	my @line = split('\t',$_);
	my $chrom = $line[0] =~ m/Chr(\d+)/;
	my $id = ".";
	my $pos = $line[1];
	my $qual = ".";
	my $filter = "PASS";
	my $info = "PROGRAM=reference_annotation;";
	my $ref = '';
	my $alt = '.';
	my $len = '';
	if ($line[3] lt 0) { # deletion
		$ref=".";
		$len=$line[3];
		$info.="SVTYPE=DEL;SVLEN=$len;";
		}
	elsif ($line[3] gt 0) { #insertion
		$ref=".";
		$len=$line[3];
		$info.="SVTYPE=INS;SVLEN=$len;";
	}
	else { die "error 0"; }

	print "$chrom\t$pos\t$id\t$ref\t$alt\t$qual\t$filter\t$info\n";
}

exit 0;
