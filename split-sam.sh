#!/bin/bash
# (c) A. Riva, 2014
# $Revision: 192 $

INFILE=$1
NLINES=$2
PREFIX=$3
A=$4

usage() {
  echo "$0 - Split SAM or BAM files into multiple, smaller files for easier processing."
  echo
  echo "Usage: $0 inputfile [nlines] [prefix] [npost]"
  echo
  echo "Options:"
  echo " inputfile | required, should be either a .sam or .bam file."
  echo " nlines    | number of lines in each output file (default: 1000000)."
  echo " prefix    | prefix of the output files (default: 'part-')."
  echo " npost     | number of letters to use in filenames postfix (see below)."
  echo
  echo "Output file names are generated by concatenating 'prefix' with the strings"
  echo "aaa, aab, aac, etc. This allows for at most 1000 output files. If this is not"
  echo "sufficient, you can increase the number of letters used with the npost argument."
  echo "For example, if the value for that argument is 4, the strings will be aaaa, aaab,"
  echo "aaac, etc (10000 max output files). Output files are written in SAM format."
  echo
  echo "After alignment, the resulting BAM files can be concatenated together with the"
  echo "samtools 'cat' or 'merge' commands. Please see samtools documentation for details."
  echo
  echo "(c) 2014, A. Riva, DiBiG, ICBR Bioinformatics, University of Florida"
}

if [ "$INFILE" == "" ] || [ "$INFILE" == "-h" ];
then
  usage
  exit 1
fi

if [ ! -f $INFILE ];
then
  echo "$0: file $INFILE does not exist or is not readable."
  exit 2
fi

if [ "$NLINES" == "" ];
then
  NLINES=1000000
fi

if [ "$PREFIX" == "" ];
then
  PREFIX="part-"
fi

if [ "$A" == "" ];
then
  A=3
fi

SAMHDR=`mktemp --tmpdir=.`
ext=${INFILE##*.}
if [ "$ext" == "sam" ];
then
    echo SAM format detected
    samtools view -S -H $INFILE > $SAMHDR
    samtools view -S $INFILE | split -a $A -l $NLINES - $PREFIX
else
    echo BAM format detected
    samtools view -H $INFILE > $SAMHDR
    samtools view $INFILE | split -a $A -l $NLINES - $PREFIX
fi

for s in `echo ${PREFIX}*`;
do
    # echo $s
    out=${s}.sam
    # echo $out
    cat $SAMHDR > $out
    cat $s >> $out
    rm -f $s
done
rm -f $SAMHDR
