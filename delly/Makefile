########################
### Pipeline Setting ###
########################

# SGE configuration.
SGE_PE = BWA

# Keep all files (Todo: In view of disk space, maybe we shouldn't do this?).
.SECONDARY:

# Delete target if recipe returns error status code.
.DELETE_ON_ERROR:

# Makefile specific settings
THIS_MAKEFILE = $(lastword $(MAKEFILE_LIST))
MAKEFILE_DIR := $(realpath $(dir $(realpath $(firstword $(MAKEFILE_LIST)))))
THIS_MAKEFILE_DIR := $(realpath $(dir $(realpath $(lastword $(MAKEFILE_LIST)))))

#####################
### Used Programs ###
#####################

include $(MAKEFILE_DIR)/../conf.mk

## Paths to tools used
DELLY_VERSION := delly-v0.2.2
DELLY_DIR = $(PROGRAMS_DIR)/delly/$(DELLY_VERSION)
DELLY := $(DELLY_DIR)/delly_v0.2.2_linux_x86_64bit

# Just for make -n
%.bam:
	@

%.delly/delly.raw.vcf: %.bam $(REFERENCE)
	mkdir -p $(dir $@)
	$(DELLY) -t DEL -o $@ -g $(word 2, $^) $<

%.delly.vcf: %.delly/delly.raw.vcf
	cp $< $@


