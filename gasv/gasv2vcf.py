import csv

variants_file = '/home/gasv/Example.bam.gasv.in.clusters'
output_file = 'gasv_bwa.vcf'

oh = open(output_file, 'w')
with open(variants_file, 'r') as ih:
    reader = csv.reader(ih, delimiter="\t")
    line = reader.next()
    for attrs in reader:
        chrom = attrs[1]
        pos = attrs[2]
        end = attrs[4]
        id = "."
        ref = "."
        var_type = attrs[7]
        qual = "."
        alt = "."
        filt = "PASS"
        var_len = int(end.split(',')[1]) - int(pos.split(',')[1]) + 1
        info = "PROGRAM=BWA,GASV;SVTYPE=%s;SVLEN=%s" % (var_type, var_len)
        vcf_list = [chrom, pos, id, ref, alt, qual, filt, info]
        vcf_line = "\t".join(vcf_list) + "\n"
        oh.write(vcf_line)

oh.close()
