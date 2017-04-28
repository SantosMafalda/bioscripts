#!/usr/bin/env python

import sys
import gzip
import os.path

import Script

__doc__ = """This is doc."""

### Program definition

def usage():
    sys.stderr.write("""countseqs.py - Count sequences in fasta/fastq files.

Usage: countseqs.py [-h] [-m] [-t] [-o outfile] files...

Prints the number of sequences contained in the specified files. Files can be 
in fasta or fastq format, optionally compressed with gzip. Output is in four 
columns (tab-delimited): filename, number of sequences, total number of 
bases, average sequence length.

Options:

-h, --help | print this usage message
-o outfile | write output to outfile (instead of standard output)
-t         | print total of all files at the end
-m         | print number of reads in millions

""")

P = Script.Script("countseqs.py", "1.0", usage=usage)

OUTPUT = sys.stdout
TOTAL = False
MILLIONS = False

def printReads(r):
    if MILLIONS:
        return "{:.1f}M".format(r/1000000.0)
    else:
        return r

def genOpen(filename, mode):
    """Generalized open() function - works on both regular files and .gz files."""
    (name, ext) = os.path.splitext(filename)
    if ext == ".gz":
        return gzip.open(filename, mode)
    else:
        return open(filename, mode)

def countSeqs(filename):
    nseqs = 0
    nbases = 0
    with genOpen(filename, "r") as f:
        line = f.readline()
        if len(line) > 0:
            if line[0] == '>':
                (nseqs, nbases) = countSeqsFasta(f)
                OUTPUT.write("{}\t{}\t{}\t{:.1f}\n".format(filename, printReads(nseqs), nbases, 1.0*nbases/nseqs))
            elif line[0] == '@':
                (nseqs, nbases) = countSeqsFastq(f)
                OUTPUT.write("{}\t{}\t{}\t{:.1f}\n".format(filename, printReads(nseqs), nbases, 1.0*nbases/nseqs))
            else:
                sys.stderr.write("Error: file `{}' is not in Fasta or FastQ format.\n".format(filename))
    return (nseqs, nbases)

def countSeqsFasta(f):
    nseqs = 1
    nbases = 0
    for line in f:
        if line[0] == '>':
            nseqs += 1
        else:
            nbases += len(line) -1
    return (nseqs, nbases)

def countSeqsFastq(f):
    nseqs = 1
    nbases = 0
    while True:
        # Skip rest of first record
        nbases += len(f.readline())-1
        f.readline()
        f.readline()
        line = f.readline()
        if line == '':
            break
        if line[0] == '@':
            nseqs += 1
    return (nseqs, nbases)

if __name__ == "__main__":
    files = []
    next = ""
    args = sys.argv[1:]
    P.standardOpts(args)
    for a in args:
        if next == '-o':
            OUTPUT = open(a, "w")
            next = ""
        elif a == '-o':
            next = a
        elif a == '-m':
            MILLIONS = True
        elif a == '-t':
            TOTAL = True
        else:
            files.append(P.isFile(a))

    if len(files) == 0:
        P.errmsg(P.NOFILE)

    try:
        total = 0
        totbases = 0
        for filename in files:
            (nseqs, nbases) = countSeqs(filename)
            total += nseqs
            totbases += nbases
        if TOTAL:
            OUTPUT.write("Total\t{}\t{}\t{:.1f}\n".format(printReads(total), totbases, 1.0*totbases/total))
    finally:
        OUTPUT.close()
