#!/usr/bin/env python
# -*- coding: utf-8

from sys import stdout
from math import log
from codecs import open
from argparse import ArgumentParser

def main():

    parser = ArgumentParser()
    parser.add_argument("seg_file", help = "segment file with term weight one query/bidword per line in tsv format")
    args = parser.parse_args()
    
    seg_file = args.seg_file

    word_dict = {}
    phrase_counter = 0.0
    with open(seg_file, "r", encoding = "utf-8") as fd:
        for line in fd:
            splited_line = line.strip().split("\t")
            if len(splited_line) != 2:
                continue
            phrase_counter += 1
            phrase_str, phrase_seg = splited_line
            for token in phrase_seg.split(""):
                word = token.split("")[0]
                if word in word_dict:
                    word_dict[word] += 1
                else:
                    word_dict[word] = 1
    for word in word_dict:
        word_dict[word] = log(phrase_counter / word_dict[word])

    with open(seg_file, "r", encoding = "utf-8") as fd:
        for line in fd:
            splited_line = line.strip().split("\t")
            if len(splited_line) != 2:
                continue
            phrase_str, phrase_seg = splited_line
            word_list = [(token.split("")[0], float(token.split("")[1])) for token in phrase_seg.split("")]
            normalize = sum([word_dict[word[0]] for word in word_list])
            res_list = []
            for word in word_list:
                res_list.append("%s/%f/%f" % (word[0], word[1], word_dict[word[0]] / normalize))
            print "%s\t%s" % (phrase_str.encode("utf-8"), " ".join(res_list).encode("utf-8"))

if __name__ == "__main__":

    main()

