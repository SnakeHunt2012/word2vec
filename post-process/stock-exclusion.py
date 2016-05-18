#!/usr/bin/env python
# -*- coding: utf-8 -*-

from re import compile, search
from copy import copy, deepcopy
from codecs import open
from argparse import ArgumentParser

DEBUG_FLAG = True

def load_stock_dict(stock_file):

    stock_dict = {}
    code_dict = {}
    prefix_dict = {} # {A: [((A, B, C), 10010]), ((A, D, E), 10011)]}
    with open(stock_file, 'r') as fd:
        for line in fd:
            splited_line = line.strip().split("\t")
            if len(splited_line) != 3:
                continue
            code, stock_str, stock_seg = splited_line
            assert code.isdigit()
            if stock_seg not in stock_dict:
                stock_dict[stock_seg] = code
            if code not in code_dict:
                code_dict[code] = stock_seg
    for stock in stock_dict:
        splited_stock = stock.split()
        if splited_stock[0] not in prefix_dict:
            prefix_dict[splited_stock[0]] = []
        prefix_dict[splited_stock[0]].append((splited_stock, stock_dict[stock]))
    return code_dict, stock_dict, prefix_dict

def is_same(list_a, list_b):

    if len(list_a) != len(list_b):
        return False
    for index in range(len(list_a)):
        if list_a[index] != list_b[index]:
            return False
    return True

def parse_code_set(code_dict, prefix_dict, query_str):

    query_code_set = set([])
    
    # extract stock code from query
    query_code_set |= (set(query_str.split()) & set(code_dict))

    # extract stock name from query
    splited_query = query_str.split()
    index = 0
    while index < len(splited_query):
        match = False
        if splited_query[index] in prefix_dict:
            for record_tuple in prefix_dict[splited_query[index]]:
                seg_list = record_tuple[0]
                if len(splited_query) - index < len(seg_list):
                    continue
                if is_same(splited_query[index:index + len(seg_list)], seg_list):
                    query_code_set.add(record_tuple[1])
                    index += len(record_tuple[0])
                    match = True
                    break
        if not match:
            index += 1
    return query_code_set

def record_replace(source_bidword, target_bidword, source_code, target_code, source_stock, target_stock):

    print "### record replace ###\t%s\t%s\t%s\t%s\t%s\t%s" % (source_bidword, target_bidword, source_code, target_code, source_stock, target_stock)

def replace_stock(code_dict, stock_dict, prefix_dict, query_code_set, bidword_str):

    splited_bidword = bidword_str.split()
    
    target_code = list(query_code_set)[0]
    for index in xrange(len(splited_bidword)):
        if (splited_bidword[index] in code_dict) and (splited_bidword[index] not in query_code_set):
            source_code = splited_bidword[index]
            source_splited_bidword = splited_bidword
            target_splited_bidword = copy(splited_bidword)
            target_splited_bidword[index] = target_code
            source_bidword = bidword_str
            target_bidword = " ".join(target_splited_bidword)
            target_bidword = target_bidword.replace(code_dict[source_code], code_dict[target_code])
            record_replace(source_bidword, target_bidword, source_code, target_code, code_dict[source_code], code_dict[target_code])
            return target_bidword

    source_code_set = parse_code_set(code_dict, prefix_dict, bidword_str) - query_code_set
    if len(source_code_set) == 0:
        return bidword_str
    source_code = list(source_code_set)[0]
    source_stock = code_dict[source_code]
    
    target_code_set = query_code_set - parse_code_set(code_dict, prefix_dict, bidword_str)
    if len(target_code_set) == 0:
        return bidword_str
    target_code = list(target_code_set)[0]
    target_stock = code_dict[target_code]
    
    source_bidword = bidword_str
    target_bidword = deepcopy(bidword_str).replace(source_stock, target_stock)
    record_replace(source_bidword, target_bidword, source_code, target_code, source_stock, target_stock)
    return target_bidword
    
def main():

    parser = ArgumentParser()
    parser.add_argument("stock_file", help = "code-stock-seg file in tsv format")
    parser.add_argument("sim_file", help = "query to bid sim file in tsv format")
    args = parser.parse_args()

    stock_file = args.stock_file
    sim_file = args.sim_file

    code_dict, stock_dict, prefix_dict = load_stock_dict(stock_file)

    outer_spliter = compile("(?<=\/[0-9].[0-9][0-9][0-9][0-9][0-9][0-9]) ")
    
    assert "300136" in parse_code_set(code_dict, prefix_dict, "信维通信")
    assert "300136" in parse_code_set(code_dict, prefix_dict, "信维通信 ")
    assert "300136" in parse_code_set(code_dict, prefix_dict, " 信维通信")
    assert "300136" in parse_code_set(code_dict, prefix_dict, "字 信维通信")
    assert "300136" in parse_code_set(code_dict, prefix_dict, "信维通信 字")
    assert "300136" not in parse_code_set(code_dict, prefix_dict, "信 维通信")
    assert "300136" not in parse_code_set(code_dict, prefix_dict, "信维通 信")
    assert "300136" not in parse_code_set(code_dict, prefix_dict, "字信维通信")
    assert "300136" not in parse_code_set(code_dict, prefix_dict, "信维通信字")
    
    assert "603822" in parse_code_set(code_dict, prefix_dict, "嘉澳 环保")
    assert "603822" in parse_code_set(code_dict, prefix_dict, "嘉澳 环保 ")
    assert "603822" in parse_code_set(code_dict, prefix_dict, " 嘉澳 环保")
    assert "603822" in parse_code_set(code_dict, prefix_dict, " 嘉澳 环保 ")
    assert "603822" not in parse_code_set(code_dict, prefix_dict, " 嘉澳环保 ")
    assert "603822" not in parse_code_set(code_dict, prefix_dict, "嘉澳环保 ")
    assert "603822" not in parse_code_set(code_dict, prefix_dict, " 嘉澳环保")
    assert "603822" not in parse_code_set(code_dict, prefix_dict, "嘉澳环保")
    
    assert "300136" in parse_code_set(code_dict, prefix_dict, "信维通信 嘉澳 环保")
    assert "603822" in parse_code_set(code_dict, prefix_dict, "信维通信 嘉澳 环保")
    assert "300136" in parse_code_set(code_dict, prefix_dict, " 信维通信 嘉澳 环保")
    assert "603822" in parse_code_set(code_dict, prefix_dict, " 信维通信 嘉澳 环保")
    assert "300136" in parse_code_set(code_dict, prefix_dict, "信维通信 嘉澳 环保 ")
    assert "603822" in parse_code_set(code_dict, prefix_dict, "信维通信 嘉澳 环保 ")
    assert "603822" not in parse_code_set(code_dict, prefix_dict, "信维通信 嘉澳环保")
    assert "603822" not in parse_code_set(code_dict, prefix_dict, "信维通信 嘉澳环保 ")
    
    assert "603822" in parse_code_set(code_dict, prefix_dict, "603822")
    assert "603822" in parse_code_set(code_dict, prefix_dict, " 603822")
    assert "603822" in parse_code_set(code_dict, prefix_dict, "603822 ")
    assert "603822" in parse_code_set(code_dict, prefix_dict, "603822 300136")
    assert "300136" in parse_code_set(code_dict, prefix_dict, "603822 300136")
    assert "603822" in parse_code_set(code_dict, prefix_dict, " 603822 300136")
    assert "300136" in parse_code_set(code_dict, prefix_dict, " 603822 300136")
    assert "603822" in parse_code_set(code_dict, prefix_dict, " 603822 300136 ")
    assert "300136" in parse_code_set(code_dict, prefix_dict, " 603822 300136 ")
    
    with open(sim_file, 'r') as fd:
        for line in fd:
            splited_line = line.strip().split("\t")
            if len(splited_line) < 2:
                continue
            query_str = splited_line.pop(0)
            bidword_str = splited_line.pop(-1)
            query_seg = query_str.split()
            bidword_list = [('/'.join(bidword.split('/')[:-1]), bidword.split('/')[-1]) for bidword in outer_spliter.split(bidword_str)] # in format [["seg seg seg", score], ["seg seg seg", score]]
            
            query_code_set = parse_code_set(code_dict, prefix_dict, query_str)
            if len(query_code_set) == 0:
                print "%s\t%s" % (query_str, bidword_str)
                continue
    
            res_list = []
            res_set = set([])
            for bidword, score in bidword_list:
                assert score.replace('.', '').isdigit()
                new_bidword = replace_stock(code_dict, stock_dict, prefix_dict, query_code_set, bidword)
                if new_bidword not in res_set:
                    res_list.append((new_bidword, score))
                    res_set.add(new_bidword)
            print "%s\t%s" % (query_str, " ".join(["%s/%s" % (bidword, score) for bidword, score in res_list]))
            

if __name__ == "__main__":

    main()

