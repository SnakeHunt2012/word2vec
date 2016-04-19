#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

    school_set = set()
    with open(tsv_file, 'r') as fd:
        for row in fd:
            splited_row = row.strip().split()
            assert len(splited_row) == 1
            school = splited_row.pop(0)
            school_set.add(school)
    synonymy_map = dict((school, school) for school in school_set)

    assert "中国地质大学（北京）" in synonymy_map
    assert "大连理工大学" in synonymy_map
    assert "复旦大学" in synonymy_map
    assert "中南财经政法大学" in synonymy_map
    assert "华中科技大学" in synonymy_map
    assert "" in synonymy_map
    assert "" in synonymy_map
    assert "" in synonymy_map
    assert "" in synonymy_map
    assert "" in synonymy_map
    assert "" in synonymy_map
    assert "" in synonymy_map
    assert "" in synonymy_map
    assert "" in synonymy_map
    assert "" in synonymy_map
    
    synonymy_map["中国地质大学"] = "中国地质大学（北京）"
    synonymy_map["大连理工"] = "大连理工大学"
    synonymy_map["上海复旦大学"] = "复旦大学"
    synonymy_map["复旦"] = "复旦大学"
    synonymy_map["中南财经"] = "中南财经政法大学"
    synonymy_map["中南财经大学"] = "中南财经政法大学"
    synonymy_map["华中理工大学"] = "华中科技大学"
    synonymy_map["华中科大"] = "华中科技大学"
    synonymy_map["华中理工"] = "华中科技大学"
    synonymy_map["华中科技"] = "华中科技大学"
    synonymy_map["华中科"] = "华中科技大学"
    synonymy_map["华中大"] = "华中科技大学"
    synonymy_map["华科大"] = "华中科技大学"
    synonymy_map["华科"] = "华中科技大学"
    synonymy_map["华中科技"] = "华中科技大学"
    synonymy_map[""] = ""
    synonymy_map[""] = ""
    synonymy_map[""] = ""
    synonymy_map[""] = ""
    synonymy_map[""] = ""
    synonymy_map[""] = ""
    synonymy_map[""] = ""
    synonymy_map[""] = ""
    synonymy_map[""] = ""
    synonymy_map[""] = ""
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
    parser.add_argument("tsv_file", help = "china school file in tsv format")
    parser.add_argument("sim_file", help = "query to bid sim file in tsv format")
    args = parser.parse_args()

    tsv_file = args.tsv_file
    sim_file = args.sim_file

    start_time = time()
    school_set, synonymy_map = load_dict(tsv_file)
    end_time = time()

    for school in school_set:
        assert school in synonymy_map

    with open(sim_file, 'r') as fd:
        for line in fd:
            splited_line = line.strip().split("\t")
            if len(splited_line) < 2:
                continue
            
            query = splited_line.pop(0)
            bidword_list = "".join(splited_line).strip(";").split(";")
        
            query_school_set = set()
            for query_seg in query.split():
                if query_seg in synonymy_map:
                    query_school_set.add(query_seg)

            if len(query_school_set) == 0:
                if not EXCLUEDE_FLAG:
                    print "%s\t%s" % (query, ";".join(bidword_list))
                continue

            res_list = []
            exc_list = [] # for debug
            for bidword in bidword_list:
                bidword_school_set = set()
                for bidword_seg in bidword.split():
                    if bidword_seg in synonymy_map:
                        bidword_school_set.add(bidword_seg)
                if len(bidword_school_set) == 0:
                    res_list.append(bidword)
                    continue
                if judge_relation(query_school_set, bidword_school_set, synonymy_map):
                    res_list.append(bidword)
                else:
                    exc_list.append(bidword)
            assert len(res_list) + len(exc_list) == len(bidword_list)

            if EXCLUEDE_FLAG:
                if len(exc_list) > 0:
                    print "%s\t%s" % (query, ";".join(exc_list))
            else:
                if len(res_list) > 0:
                    print "%s\t%s" % (query, ";".join(res_list))
                
                    
if __name__ == "__main__":

    main()

