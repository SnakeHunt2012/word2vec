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

class GeneragePhraseKernel(Thread):

    def __init__(self, seg_file, word_dict, base_number, serial_number):

        self.seg_file = seg_file
        self.word_dict = word_dict
        self.base_number = base_number
        self.serial_number = serial_number
        super(GeneragePhraseKernel, self).__init__()

    def run(self):
        
        with open(self.seg_file, "r", encoding = "utf-8") as fp:
            counter = 0
            iterator = 0
            while True:
                line = None
                try:
                    line = fp.readline()
                except Exception:
                    continue
                if not line:
                    break
                if iterator % self.base_number == self.serial_number:
                    iterator += 1
                else:
                    iterator += 1
                    continue
                bidword_str = line.strip()
                word_list = bidword_str.split()
                if word_list is None or len(word_list) == 0:
                    continue
                word_count = 0
                vector = zeros(200, dtype = "float32")
                for word in word_list:
                    if word in self.word_dict:
                        #vector += array(self.word_dict[word], dtype = "float32")
                        vector += normalize(array(self.word_dict[word], dtype = "float32"))
                        word_count += 1
                if word_count > 0:
                    vector /= word_count
                else:
                    continue
                #bidword_hash = md5(bidword_str.encode("utf-8")).hexdigest()
                #stdout.write("%s\t%s\t%s\n" % (bidword_hash, bidword_str.encode("utf-8"), " ".join([str(i) for i in vector])))
                stdout.write("%s\t%s\n" % (bidword_str.encode("utf-8"), " ".join([str(i) for i in vector])))
                stdout.flush()

class GenerageWeightedPhraseKernel(Thread):

    def __init__(self, seg_file, word_dict, base_number, serial_number):

        self.seg_file = seg_file
        self.word_dict = word_dict
        self.base_number = base_number
        self.serial_number = serial_number
        super(GenerageWeightedPhraseKernel, self).__init__()

    def run(self):
        
        with open(self.seg_file, "r", encoding = "utf-8") as fp:
            counter = 0
            iterator = 0
            for line in fp:
                if iterator % self.base_number == self.serial_number:
                    iterator += 1
                else:
                    iterator += 1
                    continue
                splited_line = line.strip().split("\t")
                if len(splited_line) != 2:
                    continue
                phrase_str, phrase_seg = splited_line
                try:
                    word_list = [(token.split("")[0], float(token.split("")[1])) for token in phrase_seg.split("")]
                except:
                    continue
                if word_list is None or len(word_list) == 0:
                    continue
                phrase_weight = 0.0
                vector = zeros(200, dtype = "float32")
                for word, weight in word_list:
                    if word in self.word_dict:
                        vector += weightlize(array(self.word_dict[word], dtype = "float32"), weight)
                        phrase_weight += weight
                if phrase_weight > 0:
                    vector /= phrase_weight
                #stdout.write("%s\t%s\n" % (" ".join([("%s[%f]") % (word, weight) for word, weight in word_list]).encode("utf-8"), " ".join([str(i) for i in vector])))
                stdout.write("%s\t%s\n" % (" ".join([word for word, weight in word_list]).encode("utf-8"), " ".join([str(i) for i in vector])))
                stdout.flush()
                
def load_dict(input_file):

    with open(input_file, "r", encoding = "utf-8") as fp:
        json_dict = loads(fp.read(), encoding = "utf-8")
    return json_dict

def generate_phrase_vector(seg_file, dict_file, thread_number = 1):

    thread_list = []
    word_dict = load_dict(dict_file)
    for i in range(thread_number):
        #thread_list.append(GeneragePhraseKernel(seg_file, word_dict, thread_number, i))
        thread_list.append(GenerageWeightedPhraseKernel(seg_file, word_dict, thread_number, i))

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()

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
    parser.add_argument("seg_file", help = "segment file with term weight one query/bidword per line in tsv format")
    args = parser.parse_args()
    
    seg_file = args.seg_file
    dict_file = args.dict_file

    generate_phrase_vector(seg_file, dict_file)

    #word_dict = load_dict(dict_file)
    #interactive(word_dict)
        

if __name__ == "__main__":

    main()

