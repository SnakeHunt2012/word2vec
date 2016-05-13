#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import getsizeof
from time import time
from codecs import open
from argparse import ArgumentParser

DEBUG_FLAG = False

def load_medical_dict(tsv_file):

    medical_set = set([])
    with open(tsv_file, 'r') as fd:
        for line in fd:
            medical_word = line.strip()
            medical_set.add(medical_word)
    return medical_set

def main():

    parser = ArgumentParser()
    parser.add_argument("tsv_file", help = "medical word dict file in tsv format")
    parser.add_argument("seg_file", help = "bidword seg file in tsv format")
    args = parser.parse_args()

    tsv_file = args.tsv_file
    seg_file = args.seg_file

    medical_set = load_medical_dict(tsv_file)

    with open(seg_file, 'r') as fd:
        for line in fd:
            splited_line = line.strip().split("\t")
            if len(splited_line) != 2:
                continue
            phrase_str, phrase_seg = splited_line
            phrase_seg_list = phrase_seg.split()
            phrase_seg_set = set(phrase_seg_list)
            if len(phrase_seg_set) == 0:
                continue
            if DEBUG_FLAG:
                if len(phrase_seg_set & medical_set) > 0:
                    print "%s\t%s" % (phrase_str, " ".join(phrase_seg_list))
                else:
                    continue
            else:
                if len(phrase_seg_set & medical_set) > 0:
                    continue
                else:
                    print "%s\t%s" % (phrase_str, " ".join(phrase_seg_list))
                

if __name__ == "__main__":

    main()

