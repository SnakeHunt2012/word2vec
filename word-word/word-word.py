#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import stdout
from codecs import open
from json import loads
from numpy import zeros
from argparse import ArgumentParser
from heapq import nlargest

import cudamat as cm

def debug(debug_str):
    stdout.write(debug_str)
    stdout.flush()

def load_dict(json_file):

    with open(json_file, "r") as fp:
        json_dict = loads(fp.read())
    return json_dict

def main():

    parser = ArgumentParser()
    parser.add_argument("json_file", help = "word2vec file in json format")
    args = parser.parse_args()

    batch_size = 1000

    json_file = args.json_file
    word_dict = load_dict(json_file)
    word_list = list(word_dict)

    word_matrix = zeros((len(word_list), 200), dtype = "float32")
    for index in xrange(len(word_list)):
        word_matrix[index, :] += word_dict[word_list[index]]

    cm.cublas_init(1000000)
    
    partition_begin = 0
    partition_end = 0
    cuda_target_matrix = cm.CUDAMatrix(word_matrix.transpose())
    while partition_begin < len(word_list):
        if (partition_begin + batch_size) > len(word_list):
            partition_end = len(word_list)
        else:
            partition_end = partition_begin + batch_size
        cuda_source_matrix = cm.CUDAMatrix(word_matrix[partition_begin:partition_end, :])
        cuda_result_matrix = cm.dot(cuda_source_matrix, cuda_target_matrix)
        result_matrix = cuda_result_matrix.asarray()
        for index in xrange(partition_end - partition_begin):
            source_word = word_list[index + partition_begin]
            sorted_list = []
            length = len(range(len(word_list)))
            sorted_list = nlargest(30, zip(result_matrix[index, :], range(len(word_list))))
            print "%s\t" % source_word.encode("utf-8"),
            for sorted_item in sorted_list:
                if (sorted_item[0] < 0.5):
                    break
                print "%s" % word_list[sorted_item[1]].encode("utf-8"),
            print
    
        partition_begin = partition_end
    
            
if __name__ == "__main__":

    main()

