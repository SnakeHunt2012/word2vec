#!/usr/bin/env python
# -*- coding: utf-8

from codecs import open
from argparse import ArgumentParser

def load_entropy_dict(entropy_file):

    entropy_dict = {}
    with open(entropy_file, 'r') as fd:
        for line in fd:
            splited_line = line.strip().split("\t")
            if len(splited_line) != 2:
                continue
            term, entropy = splited_line
            if term not in entropy_dict:
                entropy_dict[term] = float(entropy)
    return entropy_dict

def main():

    parser = ArgumentParser()
    parser.add_argument("seg_file", help = "segment file with term weight one query/bidword per line in tsv format")
    parser.add_argument("left_entropy_file", help = "word-entropy (left entropy) file in tsv format")
    parser.add_argument("right_entropy_file", help = "word-entropy (right entropy) file in tsv format")
    args = parser.parse_args()
    
    seg_file = args.seg_file
    left_entropy_file = args.left_entropy_file
    right_entropy_file = args.right_entropy_file

    left_entropy_dict = load_entropy_dict(left_entropy_file)
    right_entropy_dict = load_entropy_dict(right_entropy_file)

    with open(seg_file, 'r') as fd:
        for line in fd:
            splited_line = line.strip().split("\t")
            if len(splited_line) != 2:
                continue
            phrase_str, phrase_seg = splited_line
            word_entropy_list = [(token.split("")[0],
                                  float(token.split("")[1]),
                                  float(left_entropy_dict[token.split("")[0]]) if token.split("")[0] in left_entropy_dict else None,
                                  float(right_entropy_dict[token.split("")[0]]) if token.split("")[0] in right_entropy_dict else None)
                                 for token in phrase_seg.split("")]
            if word_entropy_list is None or len(word_entropy_list) == 0:
                continue
            print " ".join(["%s/%s/%s/%s" % (word, weight, left_entropy, right_entropy) for word, weight, left_entropy, right_entropy in word_entropy_list])
    

if __name__ == "__main__":

    main()

