#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gc import collect
from time import time
from codecs import open
from numpy import array
from numpy.random import random, random_sample
from argparse import ArgumentParser
from cudamat import cuda_set_device, cublas_init, CUDAMatrix, dot
from itertools import combinations
from heapq import nlargest

import numpy as np

DEBUG_FLAG = False

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
            #if len(line.split("\t")) != 3:
            if len(line.split("\t")) != 2:
                continue
            #md5, phrase, vector = line.split("\t")
            phrase, vector = line.split("\t")
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
            #if len(line.split("\t")) != 3:
            if len(line.split("\t")) != 2:
                continue
            #md5, phrase, vector = line.split("\t")
            phrase, vector = line.split("\t")
            if phrase in vec_dict:
                continue
            vec_dict[phrase] = index
            phrase_array = array(vector.split(), dtype = "float32")
            norm = np.sqrt(np.dot(phrase_array, phrase_array))
            if norm > 0.0:
                phrase_array /= norm
            vec_list.append(phrase_array)
            phrase_list.append(phrase)
            index += 1
    for i in xrange(len(phrase_list)):
        assert vec_dict[phrase_list[i]] == i
    assert len(vec_dict) == len(vec_list)
    return phrase_list, array(vec_list, dtype = "float32")

def sort_matrix(sim_matrix, query_list, query_index_list, bidword_list, bidword_index_list, threshold = 0.5):

    time_flag = time()
    for i in xrange(len(query_index_list)):
        length_before = len(bidword_index_list)
        sim_matrix_row = sim_matrix[i]
        bidword_index_length = len(bidword_index_list)
        sorted_list = nlargest(1500, ((sim_matrix_row[j], bidword_index_list[j]) for j in xrange(bidword_index_length) if sim_matrix_row[j] > threshold))
        length_after = len(sorted_list)
        query_string = query_list[query_index_list[i]]

        if DEBUG_FLAG:
            print "%s(%d/%d)\t" % (query_string, length_after, length_before),
            for sim_score, bidword_index in sorted_list:
                if sim_score < threshold:
                    break
                print "%s(%f)" % (bidword_list[bidword_index], sim_score),
            print
        else:
            #print "%s\t" % (query_string),
            res_list = []
            for sim_score, bidword_index in sorted_list:
                if sim_score < threshold:
                    break
                #print "%s%f;" % (bidword_list[bidword_index], sim_score),
                res_list.append("%s%f" % (bidword_list[bidword_index], sim_score))
            #print
            if len(res_list) > 0:
                print "%s\t%s" % (query_string, ";".join(res_list))
    return time() - time_flag

def main():

    parser = ArgumentParser()
    parser.add_argument("query_file", help = "word2vec file in json format")
    parser.add_argument("bidword_file", help = "word2vec file in json format")
    args = parser.parse_args()

    query_file = args.query_file
    bidword_file = args.bidword_file

    if DEBUG_FLAG:
        print "loading bidword dict ..."
    start = time()
    bidword_list, bidword_matrix = load_normalized_matrix(bidword_file)
    end = time()
    if DEBUG_FLAG:
        print "loading bidword dict done", duration(start, end)
    
    if DEBUG_FLAG:
        print "loading query dict ..."
    start = time()
    query_list, query_matrix = load_normalized_matrix(query_file)
    end = time()
    if DEBUG_FLAG:
        print "loading query dict done", duration(start, end)

    hash_length = 12
    hash_number = 1

    seed_matrix = random((200, hash_length * hash_number)) - 0.5

    if DEBUG_FLAG:
        print "initing cublas ..."
    start = time()
    cuda_set_device(1)
    cublas_init(1000000)
    end = time()
    if DEBUG_FLAG:
        print "initing cublas done", duration(start, end)

    if DEBUG_FLAG:
        print "computing hash_matrix ..."
    start = time()
    cuda_seed_matrix = CUDAMatrix(seed_matrix)
    cuda_bidword_matrix = CUDAMatrix(bidword_matrix)
    bidword_hash_matrix = dot(cuda_bidword_matrix, cuda_seed_matrix).asarray()
    del cuda_bidword_matrix
    cuda_query_matrix = CUDAMatrix(query_matrix)
    query_hash_matrix = dot(cuda_query_matrix, cuda_seed_matrix).asarray()
    del cuda_query_matrix
    end = time()
    if DEBUG_FLAG:
        print "computing hash_matrix done", duration(start, end)

    
    if DEBUG_FLAG:
        print "initing bidword_hash_dict_list ..."
    start = time()
    bidword_hash_dict_list = [dict([]) for i in xrange(hash_number)]
    end = time()
    if DEBUG_FLAG:
        print "initing bidword_hash_dict_list done", duration(start, end)
    
    if DEBUG_FLAG:
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
    if DEBUG_FLAG:
        print "aggregating bidword_hash_dict_list done", duration(start, end)

    if DEBUG_FLAG:
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
    if DEBUG_FLAG:
        print "aggregating querh_hash_dict done", duration(start, end)

    profiler_total = 0
    profiler_first = 0
    profiler_first_zero = 0
    profiler_first_one = 0
    profiler_first_two = 0
    profiler_first_three = 0
    profiler_first_four = 0
    profiler_second = 0
    profiler_third = 0
    timer = time()

    for hash_string in query_hash_dict:
        time_flag_total = time()
        time_flag_first = time()
        # random release memory
        
        if random_sample() > 0.95:
            collect()
        
        # aggregating query_index_set and bidword_index_set
        query_index_set = query_hash_dict[hash_string]
        bidword_index_set = set()
        for i in xrange(hash_number):
            time_flag_first_zero = time()
            hash_index_start = i * hash_length
            hash_index_end = hash_index_start + hash_length
            hash_key = hash_string[hash_index_start:hash_index_end]
            profiler_first_zero += time() - time_flag_first_zero
            # circum hash with hamming distance 0
            time_flag_first_one = time()
            bidword_index_set |= bidword_hash_dict_list[i][hash_key]
            profiler_first_one += time() - time_flag_first_one
            # circum hash with hamming distance 1
            time_flag_first_two = time()
            for first_index in xrange(hash_length):
                circum_hash_key = list(hash_key)
                circum_hash_key[first_index] = '1' if hash_key[first_index] == '0' else '0'
                circum_hash_key = "".join(circum_hash_key)
                if circum_hash_key in bidword_hash_dict_list[i]:
                    bidword_index_set |= bidword_hash_dict_list[i][circum_hash_key]
            profiler_first_two += time() - time_flag_first_two
            # circum hash with hamming distance 2
            time_flag_first_three = time()
            for first_index, second_index in combinations(range(hash_length), 2):
                circum_hash_key = list(hash_key)
                circum_hash_key[first_index] = '1' if hash_key[first_index] == '0' else '0'
                circum_hash_key[second_index] = '1' if hash_key[second_index] == '0' else '0'
                circum_hash_key = "".join(circum_hash_key)
                if circum_hash_key in bidword_hash_dict_list[i]:
                    bidword_index_set |= bidword_hash_dict_list[i][circum_hash_key]
            profiler_first_three += time() - time_flag_first_three
            ## circum hash with hamming distance 3
            #time_flag_first_four = time()
            #for first_index, second_index, third_index in combinations(range(hash_length), 3):
            #    circum_hash_key = list(hash_key)
            #    circum_hash_key[first_index] = '1' if hash_key[first_index] == '0' else '0'
            #    circum_hash_key[second_index] = '1' if hash_key[second_index] == '0' else '0'
            #    circum_hash_key[third_index] = '1' if hash_key[third_index] == '0' else '0'
            #    circum_hash_key = "".join(circum_hash_key)
            #    if circum_hash_key in bidword_hash_dict_list[i]:
            #        bidword_index_set |= bidword_hash_dict_list[i][circum_hash_key]
            #profiler_first_four += time() - time_flag_first_four
        # computing sim between query_index_list and bidword_index_list
        profiler_first += time() - time_flag_first
        
        query_index_list = list(query_index_set)
        bidword_index_list = list(bidword_index_set)

        partition_length = 1e8
        if DEBUG_FLAG or True:
            print "### profile ### matrix shape:", query_matrix[query_index_list, :].shape, bidword_matrix[bidword_index_list, :].transpose().shape, len(query_index_list) * len(bidword_index_list)
        if len(bidword_index_list) > partition_length:
            raise Exception("bidword_index_list too long: %d" % len(query_index_list))
        
        step = int(partition_length / len(bidword_index_list))
        partition_begin = 0
        partition_end = 0
        while partition_end < len(query_index_list):
            partition_end = len(query_index_list) if partition_begin + step > len(query_index_list) else partition_begin + step
            if DEBUG_FLAG or True:
                print "### profile ### partition_begin:", partition_begin, "partition_end:", partition_end
            time_flag_second = time()
            sim_matrix = dot(
                CUDAMatrix(query_matrix[query_index_list[partition_begin:partition_end], :]),
                CUDAMatrix(bidword_matrix[bidword_index_list, :].transpose())
            ).asarray().tolist()
            profiler_second += time() - time_flag_second
            profiler_third += sort_matrix(sim_matrix, query_list, query_index_list[partition_begin:partition_end], bidword_list, bidword_index_list)
            partition_begin = partition_end
            
        profiler_total += time() - time_flag_total
        if DEBUG_FLAG or True:
            print "### profile ### total=%f first=%f(%f)[%f(%f)%f(%f)%f(%f)%f(%f)%f(%f)] second=%f(%f) third=%f(%f) %s(%f)" % (
                profiler_total,
                profiler_first, profiler_first / profiler_total,
                profiler_first_zero, profiler_first_zero / profiler_first,
                profiler_first_one, profiler_first_one / profiler_first,
                profiler_first_two, profiler_first_two / profiler_first,
                profiler_first_three, profiler_first_three / profiler_first,
                profiler_first_four, profiler_first_four / profiler_first,
                profiler_second, profiler_second / profiler_total,
                profiler_third, profiler_third / profiler_total,
                duration(timer, time()), time() - timer
            )
    
if __name__ == "__main__":

    main()

