#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import stdout
from codecs import open
from json import loads
from numpy import zeros, dot, sqrt
from argparse import ArgumentParser
from heapq import nlargest

import cudamat as cm

def debug(debug_str):
    stdout.write(debug_str)
    stdout.flush()

def load_vector_dict(json_file):

    with open(json_file, "r") as fd:
        json_dict = loads(fd.read())

    # normalize
    for word in json_dict:
        vector = json_dict[word]
        json_dict[word] = vector / sqrt(dot(vector, vector))
    return json_dict

def load_suffix_set(tsv_file):

    suffix_set = set([])
    with open(tsv_file, "r") as fd:
        for line in fd:
            if len(line.strip().split()) != 1:
                continue
            suffix_set.add(line.strip())
    return suffix_set

def main():

    parser = ArgumentParser()
    parser.add_argument("json_file", help = "word2vec file in json format")
    parser.add_argument("tsv_file", help = "suffix word list")
    args = parser.parse_args()

    batch_size = 1000

    json_file = args.json_file
    tsv_file = args.tsv_file
    
    word_dict = load_vector_dict(json_file)
    word_list = list(word_dict)
    suffix_set = load_suffix_set(tsv_file)
    suffix_list = list(suffix_set)

    suffix_matrix = zeros((len(suffix_list), 200), dtype = "float32")
    for index in xrange(len(suffix_list)):
        if suffix_list[index].decode("utf-8") in word_dict:
            suffix_matrix[index, :] += word_dict[suffix_list[index].decode("utf-8")]

    cm.cublas_init(1000000)
    
    partition_begin = 0
    partition_end = 0
    cuda_target_matrix = cm.CUDAMatrix(suffix_matrix.transpose())
    while partition_begin < len(suffix_list):
        if (partition_begin + batch_size) > len(suffix_list):
            partition_end = len(suffix_list)
        else:
            partition_end = partition_begin + batch_size
        cuda_source_matrix = cm.CUDAMatrix(suffix_matrix[partition_begin:partition_end, :])
        cuda_result_matrix = cm.dot(cuda_source_matrix, cuda_target_matrix)
        result_matrix = cuda_result_matrix.asarray()
        for index in xrange(partition_end - partition_begin):
            source_suffix = suffix_list[index + partition_begin]
            sorted_list = []
            length = len(range(len(suffix_list)))
            sorted_list = nlargest(30, zip(result_matrix[index, :], range(len(suffix_list))))
            #print "%s\t" % source_suffix.encode("utf-8"),
            print "%s\t" % source_suffix,
            for sorted_item in sorted_list:
                if (sorted_item[0] < 0.4):
                    break
                #print "%s" % suffix_list[sorted_item[1]].encode("utf-8"),
                print "%s/%f" % (suffix_list[sorted_item[1]], sorted_item[0]),
            print
        partition_begin = partition_end
    
            
if __name__ == "__main__":

    main()

