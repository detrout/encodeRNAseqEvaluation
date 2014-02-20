#!/usr/bin/python
"""Reindex quantification filename
Copyright 2014 Diane Trout, California Institute of Technology

We discovered that some of our quantification files didn't exactly
match the file format Rafa wanted.

This program will reindex the quantification table according to Rafa's
custom GTF file.

In addition it will also the equivalent to his "sanitycheck.R" script
in the rafa_validation function.

Usage:

python reindex_quantification.py --gtf (path to gziped gtf file) \
                                 --sample (path to sampleInfo.txt file) \
                                 source quantification tab-delmited filename \
                                 target tab delimited filename
  

"""


from __future__ import print_function
import os
import numpy
import pandas as pd
import gzip
from argparse import ArgumentParser
import logging

LOGGER = logging.getLogger("Reindexer")

def main():
    parser = ArgumentParser()
    parser.add_argument('--gtf', help='specify what gtf file to use')
    parser.add_argument('--sample', help='sample info')
    parser.add_argument('infile', nargs=1, help='input quantification filename')
    parser.add_argument('outfile', nargs=1, help='output quantification filename')

    args = parser.parse_args()

    if not (args.gtf and args.sample and args.infile and args.outfile):
       parser.error("All arguments are required")

    infile = args.infile[0]
    outfile = args.outfile[0]
    
    LOGGER.info("Reading %s for feature ids", args.gtf)
    row_index = pd.Series([read_metadata(x)['feature_id'] for x in gzip.GzipFile( args.gtf, 'r' ) if x[0] != '#' ])
    LOGGER.info("Reading %s for sample names", args.sample)
    sampleinfo = pd.read_csv(args.sample, sep='\t', index_col=0)

    LOGGER.info("Reading %s", infile)
    table= pd.read_csv(infile, index_col=0, header=0, sep='\t')

    LOGGER.info("Reindexing")
    reindexed = table.reindex(row_index)
    LOGGER.info("Writing reindex table to %s", outfile)
    
    rafa_validation(reindexed, sampleinfo, row_index)
    
    reindexed.to_csv(outfile, sep="\t")

def rafa_validation(table, samples, rows):
    if not numpy.all(table.columns == samples.index):
        raise RuntimeError("column indexes don't match")
    if not numpy.all(table.index == rows):
        for i, x in enumerate(table.index == rows):
            if not x:
                print("Row {} didn't match {} != {}".format(i+1, table.index[i], rows[i]) )
        raise RuntimeError("row indexes don't match")

def read_metadata(line):
    record = line.rstrip().split("\t")
    metadata = {}
    for term in record[8].split("; "):
        name, value = term.split()
        value = value.replace('"', '')
        metadata[name] = value
    return metadata

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()