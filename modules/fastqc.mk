# Makefile - FastQC for the AllBioTC2 pipeline
#
# (c) 2013 - Wai Yi Leung
# (c) 2013 AllBio (see AUTHORS file)

MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))
include $(MAKEFILE_DIR)/fastqc.conf.mk
include $(MAKEFILE_DIR)/../conf.mk


%.fastqc: %.fastq
	mkdir -p $@;
	fastqc -format fastq -o $@ $^
