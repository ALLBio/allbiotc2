#!/usr/bin/env perl

my $filename = $ARGV[0];
open(READ, $filename) || die "failed";
while(<READ>) {
	chomp;
	my @line = split('\t',$_);
	$line[0] =~ m/Chr(\d+)/;
	my $chrom = $1;
	my $id = ".";
	my $pos = $line[3];
	my $qual = ".";
	my $filter = "PASS";
	my $info = "PROGRAM=reference_annotation;";
	my $ref = '';
	my $alt = '.';
	my $len = '';
	if ($line[1] eq 'deletion') { # deletion
		$ref=".";
		$len=$line[2];
		$info.="SVTYPE=DEL;SVLEN=$len;";
		}
	elsif ($line[1] eq 'insertion') { #insertion
		$ref=".";
		$len=$line[2];
		$info.="SVTYPE=INS;SVLEN=$len;";
		unless ($line[5] eq 'Not_confirmed') { print "$chrom\t$pos\t$id\t$ref\t$alt\t$qual\t$filter\t$info\n"; }
		$len=$line[4]-$line[3];
		$info = "PROGRAM=reference_annotation;SVTYPE=DEL;SVLEN=$len;";
	}
	else { die "error 0"; }

	unless ($line[5] eq 'Not_confirmed') { print "$chrom\t$pos\t$id\t$ref\t$alt\t$qual\t$filter\t$info\n"; }
}

exit 0;
