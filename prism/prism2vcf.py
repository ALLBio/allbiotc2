import csv

variants_file = 'bwa/prism_output/split_all.sam_ns_rmmul_cigar_sorted_sv'
output_file = 'prism_bwa.vcf'

oh = open(output_file, 'w')
with open(variants_file, 'r') as ih:
    reader = csv.reader(ih, delimiter="\t")
    line = reader.next()
    for attrs in reader:
        chrom = attrs[0]
        pos = attrs[1]
        end = attrs[2]
        id = "."
        ref = "."
        var_type = attrs[4]
        if var_type == "INS":
            alt = attrs[21]
        else:
            alt = "."
        qual = "."
        filt = "PASS"
        var_len = int(end) - int(pos) + 1
        info = "PROGRAM=BWA,PRISM;SVTYPE=%s;SVLEN=%s" % (var_type, var_len)
        vcf_list = [chrom, pos, id, ref, alt, qual, filt, info]
        vcf_line = "\t".join(vcf_list) + "\n"
        oh.write(vcf_line)

oh.close()
