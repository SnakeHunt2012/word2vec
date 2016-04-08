#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import time
from codecs import open
from numpy import array, matrix
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

def load_dict(tsv_file):

    vec_dict = {}
    with open(tsv_file, "r") as fp:
        for line in fp:
            line = line.strip()
            if len(line.split("\t")) != 3:
                continue
            md5, phrase, vector = line.split("\t")
            if phrase in vec_dict:
                continue
            vec_dict[phrase] = array(vector.split(), dtype = "float32")
    return vec_dict

def load_matrix(tsv_file):

    phrase_list = []
    vec_list = []
    vec_dict = {}
    index = 0
    with open(tsv_file, "r") as fp:
        for line in fp:
            line = line.strip()
            if len(line.split("\t")) != 3:
                continue
            md5, phrase, vector = line.split("\t")
            if phrase in vec_dict:
                continue
            vec_dict[phrase] = index
            vec_list.append(array(vector.split(), dtype = "float32"))
            phrase_list.append(phrase)
            index += 1
    for i in xrange(len(phrase_list)):
        assert vec_dict[phrase_list[i]] == i
    assert len(vec_dict) == len(vec_list)
    return phrase_list, array(vec_list, dtype = "float32")

def load_normalized_matrix(tsv_file):

    phrase_list = []
    vec_list = []
    vec_dict = {}
    index = 0
    with open(tsv_file, "r") as fp:
        for line in fp:
            line = line.strip()
            if len(line.split("\t")) != 3:
                continue
            md5, phrase, vector = line.split("\t")
            if phrase in vec_dict:
                continue
            vec_dict[phrase] = index
            phrase_array = array(vector.split(), dtype = "float32")
            phrase_array /= np.sqrt(np.dot(phrase_array, phrase_array))
            vec_list.append(phrase_array)
            phrase_list.append(phrase)
            index += 1
    for i in xrange(len(phrase_list)):
        assert vec_dict[phrase_list[i]] == i
    assert len(vec_dict) == len(vec_list)
    return phrase_list, array(vec_list, dtype = "float32")

def main():

    parser = ArgumentParser()
    parser.add_argument("query_file", help = "word2vec file in json format")
    parser.add_argument("bidword_file", help = "word2vec file in json format")
    args = parser.parse_args()

    query_file = args.query_file
    bidword_file = args.bidword_file

    print "loading bidword dict ..."
    start = time()
    bidword_list, bidword_matrix = load_normalized_matrix(bidword_file)
    end = time()
    print "loading bidword dict done", duration(start, end)
    
    print "loading query dict ..."
    start = time()
    query_list, query_matrix = load_normalized_matrix(query_file)
    end = time()
    print "loading query dict done", duration(start, end)

    hash_length = 15
    hash_number = 1

    seed_matrix = random((200, hash_length * hash_number)) - 0.5

    print "initing cublas ..."
    start = time()
    cublas_init(1000000)
    end = time()
    print "initing cublas done", duration(start, end)

    print "computing hash_matrix ..."
    start = time()
    cuda_seed_matrix = CUDAMatrix(seed_matrix)
    cuda_bidword_matrix = CUDAMatrix(bidword_matrix)
    cuda_query_matrix = CUDAMatrix(query_matrix)
    bidword_hash_matrix = dot(cuda_bidword_matrix, cuda_seed_matrix).asarray()
    query_hash_matrix = dot(cuda_query_matrix, cuda_seed_matrix).asarray()
    end = time()
    print "computing hash_matrix done", duration(start, end)

    del cuda_bidword_matrix
    del cuda_query_matrix
    
    print "initing bidword_hash_dict_list ..."
    start = time()
    bidword_hash_dict_list = [dict([]) for i in xrange(hash_number)]
    end = time()
    print "initing bidword_hash_dict_list done", duration(start, end)
    
    print "aggregating bidword_hash_dict_list ..."
    start = time()
    for i in xrange(bidword_hash_matrix.shape[0]):
        hash_string = "".join(['1' if j > 0 else '0' for j in bidword_hash_matrix[i, :]])
        for j in xrange(hash_number):
            hash_index_start = j * hash_length
            hash_index_end = hash_index_start + hash_length
            hash_key = hash_string[hash_index_start:hash_index_end]
            if hash_key in bidword_hash_dict_list[j]:
                bidword_hash_dict_list[j][hash_key].add(i)
            else:
                bidword_hash_dict_list[j][hash_key] = set([i])
    end = time()
    print "aggregating bidword_hash_dict_list done", duration(start, end)

    print "aggregating query_hash_dict ..."
    start = time()
    query_hash_dict = {}
    for i in xrange(query_hash_matrix.shape[0]):
        hash_string = "".join(['1' if j > 0 else '0' for j in query_hash_matrix[i, :]])
        if hash_string in query_hash_dict:
            query_hash_dict[hash_string].add(i)
        else:
            query_hash_dict[hash_string] = set([i])
    end = time()
    # debug
    query_counter = 0
    for hash_key in query_hash_dict:
        query_counter += len(query_hash_dict[hash_key])
    print "query counter", query_counter
    print "aggregating querh_hash_dict done", duration(start, end)

    profiler_total = 0
    profiler_first = 0
    profiler_second = 0
    profiler_third = 0

    for hash_string in query_hash_dict:
        time_flag_total = time()
        time_flag_first = time()
        # aggregating query_index_set and bidword_index_set
        query_index_set = query_hash_dict[hash_string]
        bidword_index_set = set()
        for i in xrange(hash_number):
            hash_index_start = i * hash_length
            hash_index_end = hash_index_start + hash_length
            hash_key = hash_string[hash_index_start:hash_index_end]
            # circum hash with hamming distance 0
            bidword_index_set |= bidword_hash_dict_list[i][hash_key]
            # circum hash with hamming distance 1
            for first_index in xrange(hash_length):
                circum_hash_key = list(hash_key)
                circum_hash_key[first_index] = '1' if hash_key[first_index] == '0' else '0'
                circum_hash_key = "".join(circum_hash_key)
                if circum_hash_key in bidword_hash_dict_list[i]:
                    bidword_index_set |= bidword_hash_dict_list[i][circum_hash_key]
            # circum hash with hamming distance 2
            for first_index, second_index in combinations(range(hash_length), 2):
                circum_hash_key = list(hash_key)
                circum_hash_key[first_index] = '1' if hash_key[first_index] == '0' else '0'
                circum_hash_key[second_index] = '1' if hash_key[second_index] == '0' else '0'
                circum_hash_key = "".join(circum_hash_key)
                if circum_hash_key in bidword_hash_dict_list[i]:
                    bidword_index_set |= bidword_hash_dict_list[i][circum_hash_key]
            ## circum hash with hamming distance 3
            #for first_index, second_index, third_index in combinations(range(hash_length), 3):
            #    circum_hash_key = list(hash_key)
            #    circum_hash_key[first_index] = '1' if hash_key[first_index] == '0' else '0'
            #    circum_hash_key[second_index] = '1' if hash_key[second_index] == '0' else '0'
            #    circum_hash_key[third_index] = '1' if hash_key[third_index] == '0' else '0'
            #    circum_hash_key = "".join(circum_hash_key)
            #    if circum_hash_key in bidword_hash_dict_list[i]:
            #        bidword_index_set |= bidword_hash_dict_list[i][circum_hash_key]
        profiler_first += time() - time_flag_first
        time_flag_second = time()
        # computing sim between query_index_list and bidword_index_list
        query_index_list = list(query_index_set)
        bidword_index_list = list(bidword_index_set)
        sim_matrix = dot(CUDAMatrix(query_matrix[query_index_list, :]), CUDAMatrix(bidword_matrix[bidword_index_list, :].transpose())).asarray()
        profiler_second += time() - time_flag_second
        time_flag_third = time()
        for i in xrange(len(query_index_list)):
            length_before = len(bidword_index_list)
            
            range_list = [[], [], [], [], []]
            for j in xrange(len(query_index_list)):
                range_index = int((sim_matrix[i][j] + 0.4999) * 10 - 10)
                if range_index < 0:
                    continue
                range_list[range_index].append((sim_matrix[i][j]), bidword_index_list[j])
                
            sorted_list = []
            bidword_counter = 50
            for j in [4, 3, 2, 1, 0]:
                if bidword_counter <= 0:
                    break
                if len[range_list[j]] < bidword_counter:
                    sorted_list.extend(sorted(range_list[j], reverse = True))
                    bidword_counter -= len(range_list[j])
                else:
                    sorted_list.extend(nlargest(bidword_counter, range_list[j]))
                    bidword_counter = 0
                    
            length_after = len(sorted_list)
            query_string = query_list[query_index_list[i]]
            print "%s(%d/%d)\t" % (query_string, length_after, length_before),
            for sim_score, bidword_index in sorted_list:
                if sim_score < 0.5:
                    break
                print "%s(%f)" % (bidword_list[bidword_index], sim_score),
            print
        profiler_third += time() - time_flag_third
        profiler_total += time() - time_flag_total
        print "###profile###\ttotal=%f\tfirst=%f(%f)\tsecond=%f(%f)\tthird=%f(%f)" % (profiler_total,
                                                                                      profiler_first, profiler_first / profiler_total,
                                                                                      profiler_second, profiler_second / profiler_total,
                                                                                      profiler_third, profiler_third / profiler_total)
    
if __name__ == "__main__":

    main()

