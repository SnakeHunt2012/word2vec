#!/usr/bin/env python
# -*- coding: utf-8

from re import compile
from sys import stdin

def main():

    spliter = compile("(?<=[0-9].[0-9][0-9][0-9][0-9][0-9][0-9])(;)?")
    
    for line in stdin:
        splited_line = line.strip().split("\t")
        if len(splited_line) != 2:
            continue
        query_str, bidword_list = splited_line
        bidword_list = [(' '.join(bidword.split('')[:-1]), bidword.split('')[-1]) for bidword in spliter.split(splited_line.pop(-1))]
        
        res_list = []
        exc_list = []
        query_term_set = set(query_str.split())
        query_length = sum([len(term) for term in query_term_set])
        if query_length == 0:
            continue
        for bidword, score in bidword_list:
            bidword_term_set = set(bidword.split())
            bidword_length = sum([len(term) for term in bidword_term_set])
            if bidword_length == 0:
                continue
            intersection_set = query_term_set & bidword_term_set
            intersection_length = sum([len(term) for term in intersection_set])
            query_intersection_rate = float(intersection_length) / float(query_length)
            bidword_intersection_rate = float(intersection_length) / float(bidword_length)
            if query_intersection_rate > 0.5 and bidword_intersection_rate > 0.5:
                exc_list.append("%s%s" % (bidword, score))
            else:
                res_list.append("%s%s" % (bidword, score))
        if len(res_list) > 0:
            print "%s\t%s" % (query_str, ";".join(res_list))

if __name__ == "__main__":

    main()

