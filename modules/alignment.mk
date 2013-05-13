MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))
include $(MAKEFILE_DIR)/alignment.conf.mk
# override defaults using conf.mk (which includes project.conf.mk)
include $(MAKEFILE_DIR)/../conf.mk

%.bam: $(IN)
	$(MAKE) -f $(MAKEFILE_DIR)/modules/aligners/$(ALIGNER).mk IN="$^" $@

%.bam.bai: %.bam
	$(SAMTOOLS) index $<

%.flagstat: %.bam
	$(SAMTOOLS) flagstat $< > $@

