#!/usr/bin/env python
# -*- coding: utf-8

from sys import stdout
from codecs import open
from numpy import array, zeros
from argparse import ArgumentParser
from theano import tensor, function

tensor_vector = tensor.vector()
tensor_scalar = tensor.dscalar()
normalized_vector = tensor_vector / tensor.sqrt(tensor.dot(tensor_vector, tensor_vector))
weightlized_vector = tensor_vector / tensor.sqrt(tensor.dot(tensor_vector, tensor_vector)) * tensor_scalar
normalize = function([tensor_vector], normalized_vector)
weightlize = function([tensor_vector, tensor_scalar], weightlized_vector)

def load_dict(tsv_file):

    word_dict = {}
    with open(tsv_file, "r", encoding = "utf-8") as fd:
        for line in fd:
            splited_line = line.strip().split("\t")
            if len(splited_line) != 2:
                continue
            word, vector = splited_line
            if word not in word_dict:
                word_dict[word] = [float(value) for value in vector.split()]
                assert len(word_dict[word]) == 200
    return word_dict

def generate_phrase_vector(seg_file, dict_file, shrink_flag, thread_number = 1):

    word_dict = load_dict(dict_file)
    phrase_set = set([])
    with open(seg_file, "r", encoding = "utf-8") as fp:
        for line in fp:
            splited_line = line.strip().split("\t")
            if len(splited_line) != 2:
                continue
            phrase_str, phrase_seg = splited_line
            try:
                word_list = [(token.split("")[0], float(token.split("")[1])) for token in phrase_seg.split("")]
            except:
                continue
            if shrink_flag:
                phrase_key = " ".join([word for word, score in word_list])
                if phrase_key in phrase_set:
                    continue
                else:
                    phrase_set.add(phrase_key)
            phrase_weight = 0.0
            vector = zeros(200, dtype = "float32")
            match_count = 0
            match_length = 0
            for word, weight in word_list:
                if word in word_dict:
                    vector += weightlize(array(word_dict[word], dtype = "float32"), weight)
                    phrase_weight += weight
                    match_count += 1
                    match_length += len(word.encode("utf-8"))
            if phrase_weight > 0:
                vector /= phrase_weight
            total_count = len(word_list)
            total_length = sum([len(word.encode("utf-8")) for word, weight in word_list])
            if float(match_count) / total_count >= 0.5 and float(match_length) / total_length >= 0.5:
                #stdout.write("%s\t%s\n" % (" ".join([("%s[%f]") % (word, weight) for word, weight in word_list]).encode("utf-8"), " ".join([str(i) for i in vector])))
                stdout.write("%s\t%s\n" % (" ".join([word for word, weight in word_list]).encode("utf-8"), " ".join([str(i) for i in vector])))
            #else:
            #    stdout.write("### filtered ###: %s\t%d/%d\t%d/%d\n" % (" ".join([word for word, weight in word_list]).encode("utf-8"), match_count, total_count, match_length, total_length))
            stdout.flush()

def main():

    parser = ArgumentParser()
    parser.add_argument("dict_file", help = "word2vec file in json format")
    parser.add_argument("seg_file", help = "segment file with term weight one query/bidword per line in tsv format")
    parser.add_argument("--shrink", help = "sort terms in order to shrink phrase space", action = "store_true")
    args = parser.parse_args()
    
    seg_file = args.seg_file
    dict_file = args.dict_file
    shrink_flag = args.shrink

    generate_phrase_vector(seg_file, dict_file, shrink_flag)

if __name__ == "__main__":

    main()

