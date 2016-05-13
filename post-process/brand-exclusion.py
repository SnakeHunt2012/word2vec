#!/usr/bin/env python
# -*- coding: utf-8 -*-

from re import compile
from sys import getsizeof
from time import time
from codecs import open
from numpy import array, matrix
from numpy.random import random
from argparse import ArgumentParser
from itertools import combinations
from heapq import nlargest

BRAND_EXCLUDED = False

def duration(start, end):

    second = (end - start) % 60
    minute = (end - start) % 3600 / 60
    hour = (end - start) / 3600
    return "%d:%02d:%02d" % (hour, minute, second)

def load_dict(dict_file):

    brand_set = set()
    category_dict = {}
    with open(dict_file, 'r') as fd:
        for line in fd:
            splited_line = line.split()
            if len(splited_line) < 2:
                continue
            category = int(splited_line.pop(0))
            brand = " ".join(splited_line)
            brand_set.add(brand)
            if brand in category_dict:
                category_dict[brand].add(category)
            else:
                category_dict[brand] = set([category])
    return brand_set, category_dict

def main():

    parser = ArgumentParser()
    parser.add_argument("dict_file", help = "category-brand file in space splited file format")
    parser.add_argument("sim_file", help = "query to bid sim file in tsv format")
    args = parser.parse_args()

    dict_file = args.dict_file
    sim_file = args.sim_file

    start_time = time()
    brand_set, category_dict = load_dict(dict_file)
    end_time = time()

    spliter = compile("(?<=\/[0-9].[0-9][0-9][0-9][0-9][0-9][0-9]) ")    
    with open(sim_file, 'r') as fd:
        for line in fd:
            splited_line = line.strip().split("\t")
            if len(splited_line) < 2:
                continue
            
            query = splited_line.pop(0)
            #bidword_list = "".join(splited_line).strip(";").split(";")
            bidword_list = [('/'.join(bidword.split('/')[:-1]), bidword.split('/')[-1]) for bidword in spliter.split(splited_line.pop(-1))]

            query_brand_set = set()
            query_category_set = set()
            for query_seg in query.split():
                if query_seg in category_dict:
                    query_brand_set.add(query_seg)
                    query_category_set |= category_dict[query_seg]

            res_list = []
            exc_list = []
            for bidword, score in bidword_list:
                if len(set(bidword_seg for bidword_seg in bidword.split() if bidword_seg in category_dict) & query_brand_set) > 0:
                    res_list.append("%s/%s" % (bidword, score))
                    break
                is_exclusive = False
                for bidword_seg in bidword.split():
                    if bidword_seg in category_dict:
                        if len(category_dict[bidword_seg] & query_category_set) > 0:
                            is_exclusive = True
                            exc_list.append("%s/%s" % (bidword, score))
                            break
                if not is_exclusive:
                    res_list.append("%s/%s" % (bidword, score))

            if BRAND_EXCLUDED:
                if len(exc_list) > 0:
                    print "%s\t%s" % (query, " ".join(exc_list))
            else:
                if len(res_list) > 0:
                    print "%s\t%s" % (query, " ".join(res_list))
    
if __name__ == "__main__":

    main()

