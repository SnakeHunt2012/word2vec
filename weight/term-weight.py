#!/usr/bin/env python
# -*- coding: utf-8

from codecs import open
from argparse import ArgumentParser
from math import log


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
            word_entropy_list = [[token.split("")[0],
                                  float(token.split("")[1]),
                                  float(left_entropy_dict[token.split("")[0]]) if token.split("")[0] in left_entropy_dict else None,
                                  float(right_entropy_dict[token.split("")[0]]) if token.split("")[0] in right_entropy_dict else None]
                                 for token in phrase_seg.split("")]
            if word_entropy_list is None or len(word_entropy_list) == 0:
                continue
            cross_weight = None
            if len(word_entropy_list) > 1:
                #cross_weigt = [(post_word[2] / prev_word[3] if (post_word[2] != None and prev_word[3] != None and prev_word[3] > 0.0) else None,
                #                post_word[3] / prev_word[2] if (post_word[2] != None and prev_word[3] != None and prev_word[2] > 0.0) else None)
                #               for prev_word, post_word in zip(word_entropy_list[:-1], word_entropy_list[1:])]
                cross_weight = [(None if (post_word[2] is None or prev_word[3] is None or prev_word[3] <= 0.0) else post_word[2] / prev_word[3],
                                 None if (post_word[2] is None or prev_word[3] is None or post_word[2] <= 0.0) else prev_word[3] / post_word[2])
                                for prev_word, post_word in zip(word_entropy_list[:-1], word_entropy_list[1:])]
            if cross_weight is None:
                print " ".join(["%s/%s/%s/%s" % (word, weight, left_entropy, right_entropy) for word, weight, left_entropy, right_entropy in word_entropy_list])
            else:
                length = len(word_entropy_list)
                for index in xrange(length):
                    if index != length - 1:
                        print "%s/%s/%s/%s [%s/%s]" % (word_entropy_list[index][0], word_entropy_list[index][1], word_entropy_list[index][2], word_entropy_list[index][3], cross_weight[index][0], cross_weight[index][1]),
                    else:
                        print "%s/%s/%s/%s" % (word_entropy_list[index][0], word_entropy_list[index][1], word_entropy_list[index][2], word_entropy_list[index][3])
                    
                
    

if __name__ == "__main__":

    main()

