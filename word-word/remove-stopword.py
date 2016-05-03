#!/usr/bin/env python
# -*- coding: utf-8 -*-

from codecs import open
from argparse import ArgumentParser

def load_stopword(stopword_file):

    with open(stopword_file, 'r') as fp:
        stopword_set = set(fp.read().split())
    return stopword_set

def main():

    parser = ArgumentParser()
    parser.add_argument("stopword_file", help = "stopword file splited by blank character")
    parser.add_argument("sim_file", help = "word to word sim file in tsv format")
    args = parser.parse_args()

    stopword_file = args.stopword_file
    sim_file = args.sim_file

    stopword_set = load_stopword(stopword_file)

    with open(sim_file, 'r') as fp:
        for line in fp:
            word_list = line.strip().split()
            if len(word_list) < 2:
                continue
            source_word = word_list[0]
            target_word_list = word_list[1:]
            if source_word in stopword_set:
                continue
            for stopword in target_word_list:
                if stopword in stopword_set:
                    target_word_list.remove(stopword)
            if len(target_word_list) == 0:
                continue
            print "%s\t" % source_word,
            for target_word in target_word_list:
                print "%s" % target_word,
            print
            

if __name__ == "__main__":

    main()

