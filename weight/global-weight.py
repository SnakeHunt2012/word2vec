#!/usr/bin/env python
# -*- coding: utf-8

from sys import stdout
from math import log
from codecs import open
from argparse import ArgumentParser
from numpy import mean

def main():

    parser = ArgumentParser()
    parser.add_argument("query_file", help = "query segment file (original query and segmented query) one query per line in tsv format")
    parser.add_argument("bidword_file", help = "bidword segment file (original bidword and segmented bidword) one query per line in tsv format")
    parser.add_argument("stopword_file", help = "one stopword per line in tsv format")
    args = parser.parse_args()
    
    query_file = args.query_file
    bidword_file = args.bidword_file
    stopword_file = args.stopword_file

    iter_count = 50

    word_dict = {}

    # idf
    phrase_counter = 0.0
    with open(query_file, "r", encoding = "utf-8") as fd:
        for line in fd:
            splited_line = line.strip().split("\t")
            if len(splited_line) != 2:
                continue
            phrase_counter += 1
            phrase_str, phrase_seg = splited_line
            for word in phrase_seg.split():
                if word in word_dict:
                    word_dict[word] += 1
                else:
                    word_dict[word] = 1
    with open(bidword_file, "r", encoding = "utf-8") as fd:
        for line in fd:
            splited_line = line.strip().split("\t")
            if len(splited_line) != 2:
                continue
            phrase_counter += 1
            phrase_str, phrase_seg = splited_line
            for word in phrase_seg.split():
                if word in word_dict:
                    word_dict[word] += 1
                else:
                    word_dict[word] = 1
    for word in word_dict:
        word_dict[word] = log(phrase_counter / word_dict[word])

    # context-free weight
    assist_dict = dict((word, []) for word in word_dict)
    for i in xrange(iter_count):
        with open(query_file, "r", encoding = "utf-8") as fd:
            for line in fd:
                splited_line = line.strip().split("\t")
                if len(splited_line) != 2:
                    continue
                phrase_str, phrase_seg = splited_line
                word_set = set(phrase_seg.split())
                weight_sum = sum([word_dict[word] for word in word_set if word in word_dict])
                for word in word_set:
                    if word in assist_dict:
                        assist_dict[word].append(word_dict[word] / weight_sum)
        with open(bidword_file, "r", encoding = "utf-8") as fd:
            for line in fd:
                splited_line = line.strip().split("\t")
                if len(splited_line) != 2:
                    continue
                phrase_str, phrase_seg = splited_line
                word_set = set(phrase_seg.split())
                weight_sum = sum([word_dict[word] for word in word_set if word in word_dict])
                for word in word_set:
                    if word in assist_dict:
                        assist_dict[word].append(word_dict[word] / weight_sum)
        for word in word_dict:
            if word in assist_dict:
                word_dict[word] = mean(assist_dict[word])
            assist_dict[word] = []
                    
    # remove stopwords
    with open(stopword_file, "r", encoding = "utf-8") as fd:
        for line in fd:
            splited_line = line.strip().split("\t")
            if len(splited_line) != 1:
                continue
            stopword = splited_line[0]
            if stopword in word_dict:
                word_dict[stopword] = 0.0

    for word in word_dict:
        print "%s\t%f" % (word.encode("utf-8"), word_dict[word])


if __name__ == "__main__":

    main()

