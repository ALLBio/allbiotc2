#!/bin/bash

# Do some preprocessing on the SRA

fastq-dump --split-3 ERR031544.sra

# Run Sickle on the raw .fastq files, trim off lower quality read(parts) < Q30

/virdir/Scratch/software/sickle-master/sickle pe -f ERR031544_1.fastq -r ERR031544_2.fastq -t sanger -o ERR031544_1.trimmed.fastq -p ERR031544_2.trimmed.fastq -s ERR031544_2.singles.fastq -q 30 -l 25 > ERR031544.filtersync.stats

