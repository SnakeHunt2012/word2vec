#!/usr/bin/env python
# -*- coding: utf-8 -*-

from re import compile
from time import time
from codecs import open
from argparse import ArgumentParser

EXCLUEDE_FLAG = False

def duration(start, end):

    second = (end - start) % 60
    minute = (end - start) % 3600 / 60
    hour = (end - start) / 3600
    return "%d:%02d:%02d" % (hour, minute, second)

def load_dict(tsv_file):

    school_dict = {}
    with open(tsv_file, 'r') as fd:
        for row in fd:
            splited_row = row.strip().split()
            assert len(splited_row) > 0
            school_dict[splited_row[0]] = set(splited_row[1:])
    school_set = set(school_dict)
    
    synonymy_map = {}
    for school in school_set:
        synonymy_map[school] = school
        for syn_school in school_dict[school]:
            if syn_school in synonymy_map:
                #raise Exception("%s already in synonymy_map[%s] = %s not %s" % (syn_school, syn_school, synonymy_map[syn_school], school))
                continue
            synonymy_map[syn_school] = school
    return school_set, synonymy_map

def judge_relation(query_school_set, bidword_school_set, synonymy_map):

    source_set = set()
    for school in query_school_set:
        source_set.add(synonymy_map[school])
        
    target_set = set()
    for school in bidword_school_set:
        target_set.add(synonymy_map[school])

    return source_set.issubset(target_set)
    
def main():

    parser = ArgumentParser()
    parser.add_argument("tsv_file", help = "china school file with its synonymy in tsv format")
    parser.add_argument("sim_file", help = "query to bid sim file in tsv format")
    args = parser.parse_args()

    tsv_file = args.tsv_file
    sim_file = args.sim_file

    start_time = time()
    school_set, synonymy_map = load_dict(tsv_file)
    end_time = time()

    for school in school_set:
        assert school in synonymy_map

    spliter = compile("(?<=\/[0-9].[0-9][0-9][0-9][0-9][0-9][0-9]) ")
    with open(sim_file, 'r') as fd:
        for line in fd:
            splited_line = line.strip().split("\t")
            if len(splited_line) < 2:
                continue
            
            query = splited_line.pop(0)
            #bidword_list = "".join(splited_line).strip(";").split(";")
            bidword_list = [('/'.join(bidword.split('/')[:-1]), bidword.split('/')[-1]) for bidword in spliter.split(splited_line.pop(-1))]            
        
            query_school_set = set()
            for query_seg in query.split():
                if query_seg in synonymy_map:
                    query_school_set.add(query_seg)

            if len(query_school_set) == 0:
                if not EXCLUEDE_FLAG:
                    print "%s\t%s" % (query, " ".join(["%s/%s" % (bidword, score) for bidword, score in bidword_list]))
                continue

            res_list = []
            exc_list = [] # for debug
            for bidword, score in bidword_list:
                bidword_school_set = set()
                for bidword_seg in bidword.split():
                    if bidword_seg in synonymy_map:
                        bidword_school_set.add(bidword_seg)
                if len(bidword_school_set) == 0:
                    res_list.append("%s/%s" % (bidword, score))
                    continue
                if judge_relation(query_school_set, bidword_school_set, synonymy_map):
                    res_list.append("%s/%s" % (bidword, score))
                else:
                    exc_list.append("%s/%s" % (bidword, score))
            assert len(res_list) + len(exc_list) == len(bidword_list)

            if EXCLUEDE_FLAG:
                if len(exc_list) > 0:
                    print "%s\t%s" % (query, " ".join(exc_list))
            else:
                if len(res_list) > 0:
                    print "%s\t%s" % (query, " ".join(res_list))
                
                    
if __name__ == "__main__":

    main()

