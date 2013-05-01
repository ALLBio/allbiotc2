###	USAGE:
###		python gasv2vcf.py [variants_file] [output_file] [BWA/BT2]
###
import csv
import sys

variants_file = sys.argv[1]
output_file = sys.argv[2]
prog = "GASV,%s" % sys.argv[3]

oh = open(output_file, 'w')
with open(variants_file, 'r') as ih:
    reader = csv.reader(ih, delimiter="\t")
    line = reader.next()
    for attrs in reader:
        chrom = attrs[1]
        pos1 = attrs[2]
	pos = pos1.split(',')[0]
        end1 = attrs[4]
	end =end1.split(',')[0]
        id = "."
        ref = "."
	vt = attrs[7]
	if vt == "D":
            var_type = "DEL"
	elif vt == "I":
            var_type = "INV"
	elif vt == "IR":
            var_type = "INV"
	elif vt == "I+":
            var_type = "INV"
	elif vt == "I-":
            var_type = "INV"
	elif vt == "V":
            var_type = "DIV"
	elif vt == "T":
            var_type = "TRN"
	elif vt == "TR":
            var_type = "TRN"
	elif vt == "TN":
            var_type = "TRN"       
	qual = "."
        alt = "."
        filt = "PASS"
        var_len = int(end) - int(pos)
        info = "PROGRAM=%s,GASV;SVTYPE=%s;SVLEN=%s" % (prog, var_type, var_len)
        vcf_list = [chrom, pos, id, ref, alt, qual, filt, info]
        vcf_line = "\t".join(vcf_list) + "\n"
        oh.write(vcf_line)

oh.close()
