#!/usr/bin/env python
# -*- coding: utf-8

from codecs import open
from argparse import ArgumentParser

DEBUG_FLAG = False

def load_weight_dict(weight_file):

    weight_dict = {}
    with open(weight_file, 'r') as fd:
        for line in fd:
            splited_line = line.strip().split()
            if len(splited_line) != 2:
                continue
            word, weight = splited_line
            if word not in weight_dict:
                weight_dict[word] = float(weight)
    return weight_dict

def main():

    parser = ArgumentParser()
    parser.add_argument("weight_file", help = "word-weight in tsv format")
    parser.add_argument("phrase_file", help = "phrase segment file (original phrase and segmented phrase) one phrase per line in tsv format")
    args = parser.parse_args()

    phrase_file = args.phrase_file
    weight_file = args.weight_file

    weight_dict = load_weight_dict(weight_file)
    word_set = set(weight_dict)

    phrase_key_set = set([])
    with open(phrase_file, 'r') as fd:
        for line in fd:
            splited_line = line.strip().split("\t")
            if len(splited_line) != 2:
                continue
            phrase_str, phrase_seg = splited_line
            phrase_seg_list = phrase_seg.split()

            # uniq
            phrase_key = " ".join(phrase_seg_list)
            if phrase_key in phrase_key_set:
                continue
            else:
                phrase_key_set.add(phrase_key)
            
            phrase_seg_set = set(phrase_seg_list)
            outside_word_set = phrase_seg_set - word_set
            if len(outside_word_set) > 0:
                if DEBUG_FLAG:
                    print "### outsidewords ###", " ".join(list(outside_word_set))
                for word in outside_word_set:
                    weight_dict[word] = 0.0
            weight_sum = sum([weight_dict[word] for word in phrase_seg_list])
            if weight_sum == 0.0:
                res_list = ["%s%s" % (word, 1.0 / len(phrase_seg_list)) for word in phrase_seg_list]
            else:
                res_list = ["%s%s" % (word, weight_dict[word] / weight_sum) for word in phrase_seg_list]
            print "%s\t%s" % (phrase_key, "".join(res_list))
    
    
if __name__ == "__main__":

    main()

