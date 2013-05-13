
# Stampy.
STAMPY := python /usr/local/stampy/stampy-1.0.20/stampy.py

MP_INSERTSIZE=-2500
MP_INSERTSIZE_SD=500

STAMPY_REFERENCE_PATH	:= /usr/local/Genomes/H.Sapiens/hg19_sorted/stampy
STAMPY_INDEX			:= $(STAMPY_REFERENCE_PATH)/reference.fa
STAMPY_HASH				:= $(STAMPY_REFERENCE_PATH)/reference.fa

BWA_REFERENCE_PATH	:= /data/DIV5/SASC/common/Genomes/H.Sapiens/hg19_sorted/bwa-0.6.0
REFERENCE_BWA		:= $(BWA_REFERENCE_PATH)/reference.fa
REFERENCE			:= $(BWA_REFERENCE_PATH)/reference.fa

