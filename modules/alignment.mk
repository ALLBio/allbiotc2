MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))
include $(MAKEFILE_DIR)/alignment.conf.mk
# override defaults using conf.mk (which includes project.conf.mk)
include $(MAKEFILE_DIR)/../conf.mk

%.sam: $(IN)
	echo $(shell pwd)
	$(MAKE) -f $(MAKEFILE_DIR)/modules/aligners/$(ALIGNER).mk IN="$^" $@

%.bam: $(IN)
	echo $(shell pwd)
	$(MAKE) -f $(MAKEFILE_DIR)/modules/aligners/$(ALIGNER).mk IN="$^" $@

%.bam.bai: %.bam
	$(SAMTOOLS) index $<

%.flagstat: %.bam
	$(SAMTOOLS) flagstat $< > $@

.PHONY: test

test:
	$(shell pwd)
