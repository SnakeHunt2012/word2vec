#!/usr/bin/env python
# -*- coding: utf-8

from codecs import open
from argparse import ArgumentParser

DEBUG_FLAG = False

def load_suffix_set(tsv_file):

    suffix_set = set([])
    with open(tsv_file, 'r') as fd:
        for line in fd:
            suffix_set.add(line.strip())
    return suffix_set

def load_stopword_set(tsv_file):

    stopword_set = set([])
    with open(tsv_file, 'r') as fd:
        for line in fd:
            stopword_set.add(line.strip())
    return stopword_set

def main():

    parser = ArgumentParser()
    parser.add_argument("stopword_file", help = "stopword file in tsv format")
    parser.add_argument("suffix_file", help = "word-weight in tsv format")
    parser.add_argument("seg_file", help = "phrase segment file (original phrase and segmented phrase) one phrase per line in tsv format")
    args = parser.parse_args()

    stopword_file = args.stopword_file
    suffix_file = args.suffix_file
    seg_file = args.seg_file

    suffix_set = load_suffix_set(suffix_file)
    stopword_set = load_stopword_set(stopword_file)

    with open(seg_file, 'r') as fd:
        for line in fd:
            splited_line = line.strip().split("\t")
            if len(splited_line) != 2:
                continue
            phrase_str, phrase_seg = splited_line
            phrase_seg_list = phrase_seg.split()
            if len(phrase_seg_list) == 0:
                continue
            while len(phrase_seg_list) > 1 and phrase_seg_list[-1] in suffix_set:
                phrase_seg_list = phrase_seg_list[:-1]
            if len(phrase_seg_list) == 0:
                continue
            phrase_seg_list = [word for word in phrase_seg_list if word not in stopword_set]
            if DEBUG_FLAG:
                if len(phrase_seg_list) != len(phrase_seg.split()):
                    print "%s\t%s" % (phrase_str, " ".join(phrase_seg_list))
            else:
                print "%s\t%s" % (phrase_str, " ".join(phrase_seg_list))
            

if __name__ == "__main__":

    main()

