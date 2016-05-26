#!/usr/bin/env python
# -*- coding: utf-8

from sys import stdin, stdout
from threading import Thread
from codecs import open
from json import loads
from numpy import array, zeros, dot, sqrt
from hashlib import md5
from argparse import ArgumentParser
from progressbar import ProgressBar, Bar
from theano import tensor, function

tensor_vector = tensor.vector()
tensor_scalar = tensor.dscalar()
normalized_vector = tensor_vector / tensor.sqrt(tensor.dot(tensor_vector, tensor_vector))
weightlized_vector = tensor_vector / tensor.sqrt(tensor.dot(tensor_vector, tensor_vector)) * tensor_scalar
normalize = function([tensor_vector], normalized_vector)
weightlize = function([tensor_vector, tensor_scalar], weightlized_vector)

                
#def load_dict(input_file):
#
#    with open(input_file, "r", encoding = "utf-8") as fp:
#        json_dict = loads(fp.read(), encoding = "utf-8")
#    return json_dict

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

def print_word_length(word_dict, word):
    if word not in word_dict:
        print word, "not in dict"
        return
    word_vector = array(word_dict[word], dtype="float32")
    print sqrt(dot(word_vector, word_vector))

def print_phrase_sim(word_dict, phrase_one, phrase_two):
    word_list_one = phrase_one.split("+")
    word_list_two = phrase_two.split("+")
    for word in word_list_one + word_list_two:
        if word not in word_dict:
            print word, "not in dict"
            return

    word_count = 0
    vector = zeros(200, dtype = "float32")
    for word in word_list_one:
        if word in word_dict:
            vector += array(word_dict[word], dtype = "float32")
            word_count += 1
    if word_count > 0:
        vector /= word_count
    word_one_vector = vector
        
    word_count = 0
    vector = zeros(200, dtype = "float32")
    for word in word_list_two:
        if word in word_dict:
            vector += array(word_dict[word], dtype = "float32")
            word_count += 1
    if word_count > 0:
        vector /= word_count
    word_two_vector = vector
        
    word_one_length = sqrt(dot(word_one_vector, word_one_vector))
    word_two_length = sqrt(dot(word_two_vector, word_two_vector))
    print dot(word_one_vector, word_two_vector) / word_one_length / word_two_length

def interactive(word_dict):

    print "Usage: input \"word\" for vector length or \"word+word word+word\" for sim score"
    while True:
        line = stdin.readline().strip().decode("utf-8")
        if len(line.split()) == 1:
            print_word_length(word_dict, line.split()[0])
        
        if len(line.split()) == 2:
            print_phrase_sim(word_dict, line.split()[0], line.split()[1])

def main():

    parser = ArgumentParser()
    parser.add_argument("dict_file", help = "word2vec file in json format")
    args = parser.parse_args()
    
    dict_file = args.dict_file

    word_dict = load_dict(dict_file)
    interactive(word_dict)

if __name__ == "__main__":

    main()

