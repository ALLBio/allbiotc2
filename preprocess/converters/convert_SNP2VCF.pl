#!/usr/bin/env perl

my $filename = $ARGV[0];
open(READ, $filename) || die "failed";
while(<READ>) {
	chomp;
	$filename =~ m/chr(\d)/;
	my $chrom = $1;
	my @line = split('\t',$_);
	my $id = ".";
	my $pos = $line[0];
	my $qual = ".";
	my $filter = "PASS";
	my $info = "PROGRAM=reference_annotation;";
	my $ref = $line[1];
	my $alt = $line[2];
	my $len = '';
	#if ($line[3] lt 0) { # deletion
	#	$ref=".";
	#	$len=$line[3];
	#	$info.="SVTYPE=DEL;SVLEN=$len;";
	#	}
	#elsif ($line[3] gt 0) { #insertion
	#	$ref=".";
	#	$len=$line[3];
	#	$info.="SVTYPE=INS;SVLEN=$len;";
	#}
	#else { die "error 0"; }

	print "$chrom\t$pos\t$id\t$ref\t$alt\t$qual\t$filter\t$info\n";
}

exit 0;
