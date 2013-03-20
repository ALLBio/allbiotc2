
#bwa index -a bwtsw TAIR9_chr_all.fas 

bwa aln -t 4 reference/TAIR9_chr_all.fas ERR031544_1.trimmed.fastq > Ler-bwa-1.sai
bwa aln -t 4 reference/TAIR9_chr_all.fas ERR031544_2.trimmed.fastq > Ler-bwa-2.sai

bwa sampe -n25 -N25 reference/TAIR9_chr_all.fas Ler-bwa-1.sai Ler-bwa-2.sai ERR031544_1.fastq ERR031544_2.fastq > Ler-bwa.sam
samtools view -bST reference/TAIR9_chr_all.fas -o Ler-bwa.bam Ler-bwa.sam
samtools sort Ler-bwa.bam Ler-bwa.sort
samtools index Ler-bwa.sort.bam


