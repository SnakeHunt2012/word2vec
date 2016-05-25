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
                phrase_weight = 0.0
                vector = zeros(200, dtype = "float32")
                match_count = 0
                match_length = 0
                for word, weight in word_list:
                    if word in self.word_dict:
                        vector += weightlize(array(self.word_dict[word], dtype = "float32"), weight)
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

def main():

    parser = ArgumentParser()
    parser.add_argument("dict_file", help = "word2vec file in json format")
    parser.add_argument("seg_file", help = "segment file with term weight one query/bidword per line in tsv format")
    args = parser.parse_args()
    
    seg_file = args.seg_file
    dict_file = args.dict_file

    generate_phrase_vector(seg_file, dict_file)

if __name__ == "__main__":

    main()

