#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import time
from codecs import open
from json import loads
from numpy import zeros, matrix
from numpy.random import random
from argparse import ArgumentParser
from cudamat import cublas_init, CUDAMatrix, dot
from itertools import combinations
from heapq import nlargest

import numpy as np

def duration(start, end):

    second = (end - start) % 60
    minute = (end - start) % 3600 / 60
    hour = (end - start) / 3600
    return "%d:%02d:%02d" % (hour, minute, second)

def load_dict(json_file):

    with open(json_file, "r") as fp:
        json_dict = loads(fp.read())
    return json_dict

def main():

    parser = ArgumentParser()
    parser.add_argument("json_file", help = "word2vec file in json format")
    args = parser.parse_args()

    hash_length = 12
    hash_number = 2

    print "loading word_dict ..."
    start = time()
    json_file = args.json_file
    word_dict = load_dict(json_file)
    word_list = list(word_dict)
    end = time()
    print "loading word_dict done", duration(start, end)

    word_matrix = zeros((len(word_list), 200), dtype = "float32")
    seed_matrix = random((200, hash_length * hash_number)) - 0.5

    print "aggregating word_matrix ..."
    start = time()
    for index in xrange(len(word_list)):
        word_matrix[index, :] += word_dict[word_list[index]]
    end = time()
    print "aggregating word_matrx done", duration(start, end)

    print "initing cublas ..."
    start = time()
    cublas_init(1000000)
    end = time()
    print "initing cublas done", duration(start, end)

    print "computing hash_matrix ..."
    start = time()
    cuda_word_matrix = CUDAMatrix(word_matrix)
    cuda_seed_matrix = CUDAMatrix(seed_matrix)
    hash_matrix = dot(cuda_word_matrix, cuda_seed_matrix).asarray()
    end = time()
    print "computing hash_matrix done", duration(start, end)

    print "initing hash_list/hash_dict_list ..."
    start = time()
    #hash_list = [[[] for j in xrange(hash_number)] for i in xrange(len(word_list))]
    hash_dict_list = [dict([]) for i in xrange(hash_number)]
    end = time()
    print "initing hash_list/hash_dict_list done", duration(start, end)
    
    print "aggregating hash_list/hash_dict_list ..."
    start = time()
    for i in xrange(len(word_list)):
        hash_string = "".join(['1' if j > 0 else '0' for j in hash_matrix[i, :]])
        for j in xrange(hash_number):
            hash_index_start = j * hash_length
            hash_index_end = hash_index_start + hash_length
            
            # charging hash_list
            #hash_list[i][j] = hash_string[hash_index_start:hash_index_end]
            
            # Charging Hash_Dict_List
            hash_key = hash_string[hash_index_start:hash_index_end]
            if hash_key in hash_dict_list[j]:
                hash_dict_list[j][hash_key].add(i)
            else:
                hash_dict_list[j][hash_key] = set([i])
    end = time()
    print "aggregating hash_list done", duration(start, end)

    word_matrix = matrix(word_matrix)
    for i in xrange(len(word_list)):
        hash_string = "".join(['1' if j > 0 else '0' for j in hash_matrix[i, :]])
        word_string = word_list[i]
        candidate_index_set = set([])
        for j in xrange(hash_number):
            hash_index_start = j * hash_length
            hash_index_end = hash_index_start + hash_length
            hash_key = hash_string[hash_index_start:hash_index_end]
            # exact hash
            candidate_index_set.update(hash_dict_list[j][hash_key])
            # circum hash with hamming distance 1
            for k in xrange(hash_length):
                circum_hash_key = list(hash_key)
                circum_hash_key[k] = '1' if hash_key[k] == '0' else '0'
                circum_hash_key = "".join(circum_hash_key)
                if circum_hash_key in hash_dict_list[j]:
                    candidate_index_set.update(hash_dict_list[j][circum_hash_key])
            # circum hash with hamming distance 2
            for pre_index, post_index in combinations(range(hash_length), 2):
                circum_hash_key = list(hash_key)
                circum_hash_key[pre_index] = '1' if hash_key[pre_index] == '0' else '0'
                circum_hash_key[post_index] = '1' if hash_key[post_index] == '0' else '0'
                circum_hash_key = "".join(circum_hash_key)
                if circum_hash_key in hash_dict_list[j]:
                    candidate_index_set.update(hash_dict_list[j][circum_hash_key])
            # circum hash with hamming distance 3
            for first_index, second_index, third_index in combinations(range(hash_length), 3):
                circum_hash_key = list(hash_key)
                circum_hash_key[first_index] = '1' if hash_key[first_index] == '0' else '0'
                circum_hash_key[second_index] = '1' if hash_key[second_index] == '0' else '0'
                circum_hash_key[third_index] = '1' if hash_key[third_index] == '0' else '0'
                circum_hash_key = "".join(circum_hash_key)
                if circum_hash_key in hash_dict_list[j]:
                    candidate_index_set.update(hash_dict_list[j][circum_hash_key])
        candidate_index_list = list(candidate_index_set)
        source_matrix = word_matrix[i, :]
        target_matrix = word_matrix[candidate_index_list, :].transpose()
        sim_matrix = np.dot(source_matrix, target_matrix)
        sorted_list = zip(sim_matrix[0, :].tolist()[0], candidate_index_list)
        print "%s(%d)\t" % (word_string.encode("utf-8"), len(sorted_list)),
        sorted_list = nlargest(50, sorted_list)
        for sim_score, word_index in sorted_list:
            if sim_score < 0.5:
                break
            print "%s(%f)" % (word_list[word_index].encode("utf-8"), sim_score),
        print
    
if __name__ == "__main__":

    main()

