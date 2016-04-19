#!/usr/bin/env python
# -*- coding: utf-8

from sys import stdout
from threading import Thread
from codecs import open
from json import loads
from numpy import array, zeros, dot, sqrt
from hashlib import md5
from argparse import ArgumentParser
from progressbar import ProgressBar, Bar

class DBLoadBidwordKernel(Thread):

    def __init__(self, seg_file, word_dict, base_number, serial_number):

        self.seg_file = seg_file
        self.word_dict = word_dict
        self.base_number = base_number
        self.serial_number = serial_number
        super(DBLoadBidwordKernel, self).__init__()

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
                bidword_str = line.strip()
                word_list = bidword_str.split()
                if word_list is None or len(word_list) == 0:
                    continue
                word_count = 0
                vector = zeros(200, dtype = "float32")
                for word in word_list:
                    if word in self.word_dict:
                        vector += array(self.word_dict[word], dtype = "float32")
                        word_count += 1
                if word_count > 0:
                    vector /= word_count
                else:
                    continue
                bidword_hash = md5(bidword_str.encode("utf-8")).hexdigest()
                stdout.write("%s\t%s\t%s\n" % (bidword_hash, bidword_str.encode("utf-8"), " ".join([str(i) for i in vector])))
                stdout.flush()

def load_dict(input_file):

    with open(input_file, "r", encoding = "utf-8") as fp:
        json_dict = loads(fp.read(), encoding = "utf-8")
    return json_dict

def hive_load_bidword(seg_file, dict_file, thread_number = 1):

    thread_list = []
    word_dict = load_dict(dict_file)
    for i in range(thread_number):
        thread_list.append(DBLoadBidwordKernel(seg_file, word_dict, thread_number, i))

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()

def main():

    parser = ArgumentParser()
    parser.add_argument("seg_file", help = "segment file with term weight one query/bidword per line in tsv format")
    parser.add_argument("dict_file", help = "word2vec file in json format")
    args = parser.parse_args()
    
    seg_file = args.seg_file
    dict_file = args.dict_file

    hive_load_bidword(seg_file, dict_file)
    

if __name__ == "__main__":

    main()

