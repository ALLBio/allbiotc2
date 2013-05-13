MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))
include $(MAKEFILE_DIR)/fastqc.conf.mk
include $(MAKEFILE_DIR)/../conf.mk


%.fastqc: %.fastq
	mkdir -p $@;
	fastqc -format fastq -o $@ $^
