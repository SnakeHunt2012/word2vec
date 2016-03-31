#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import stdout
from codecs import open
from json import loads
from numpy import zeros, array
from numpy.random import random, random_sample
from argparse import ArgumentParser
from cudamat import cublas_init, CUDAMatrix, dot

import numpy as np


def load_dict(json_file):

    with open(json_file, "r") as fp:
        json_dict = loads(fp.read())
    return json_dict

def main():

    parser = ArgumentParser()
    parser.add_argument("json_file", help = "word2vec file in json format")
    args = parser.parse_args()

    hash_length = 10
    hash_number = 3

    json_file = args.json_file
    word_dict = load_dict(json_file)
    word_list = list(word_dict)

    word_matrix = zeros((len(word_list), 200), dtype = "float32")
    seed_matrix = random((200, hash_length * hash_number)) - 0.5
    
    # +1 / -1
    #seed_matrix = []
    #for i in range(200):
    #    seed_matrix.append([])
    #    for j in range(hash_length * hash_number):
    #        if random_sample() > 0.5:
    #            seed_matrix[i].append(1)
    #        else:
    #            seed_matrix[i].append(0)
    #
    #seed_matrix = array(seed_matrix)
    #print seed_matrix
    
    for index in xrange(len(word_list)):
        word_matrix[index, :] += word_dict[word_list[index]]

    # random select word vectors as seed_matrix
    #seed_matrix = word_matrix[1000:1000 + hash_length * hash_number, :]
    #seed_matrix = seed_matrix.transpose()

    cublas_init(1000000)

    cuda_word_matrix = CUDAMatrix(word_matrix)
    cuda_seed_matrix = CUDAMatrix(seed_matrix)
    hash_matrix = dot(cuda_word_matrix, cuda_seed_matrix).asarray()

    hash_list = [[[] for j in xrange(hash_number)] for i in xrange(len(word_list))]
    for i in xrange(len(word_list)):
        hash_string = "".join(['1' if j > 0 else '0' for j in hash_matrix[i, :]])
        for j in xrange(hash_number):
            hash_index_start = j * hash_length
            hash_index_end = hash_index_start + hash_length
            hash_list[i][j] = hash_string[hash_index_start:hash_index_end]

    for i in xrange(len(word_list)):
        source_word_string = word_list[i]
        source_word_vector = word_dict[word_list[i]]
        match_list = []
        print "%s\t" % source_word_string.encode("utf-8"),
        for j in xrange(len(word_list)):
            # hash xor
            #source_word_xor = 0
            #target_word_xor = 0
            #for k in xrange(hash_number):
            #    source_word_xor ^= int(hash_list[i][k], 2)
            #    target_word_xor ^= int(hash_list[j][k], 2)
            #if source_word_xor == target_word_xor:
            #    target_word_vector = word_dict[word_list[j]]
            #    sim_score = np.dot(source_word_vector, target_word_vector) / np.sqrt(np.dot(source_word_vector, source_word_vector)) / np.sqrt(np.dot(target_word_vector, target_word_vector))
            #    if (sim_score > 0.5):
            #        match_list.append((sim_score, j))
            #    continue
            for k in xrange(hash_number):
                if hash_list[i][k] == hash_list[j][k]:
                    target_word_vector = word_dict[word_list[j]]
                    sim_score = np.dot(source_word_vector, target_word_vector) / np.sqrt(np.dot(source_word_vector, source_word_vector)) / np.sqrt(np.dot(target_word_vector, target_word_vector))
                    if (sim_score > 0.5):
                        match_list.append((sim_score, j))
                    break
        match_list = list(set(match_list))
        match_list.sort(lambda x, y: cmp(x[0], y[0]), reverse = True)
        for sim_score, j in match_list:
            target_word_string = word_list[j]
            print "%s(%f)" % (target_word_string.encode("utf-8"), sim_score),
        print


if __name__ == "__main__":

    main()

