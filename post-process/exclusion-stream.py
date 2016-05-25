#!/usr/bin/env python
# -*- coding: utf-8 -*-

from re import compile
from copy import copy, deepcopy
from codecs import open
from itertools import product
from sys import stdin, argv

DEBUG_FLAG = False

def duration(start, end):

    second = (end - start) % 60
    minute = (end - start) % 3600 / 60
    hour = (end - start) / 3600
    return "%d:%02d:%02d" % (hour, minute, second)

def load_brand_dict(dict_file):

    brand_set = set()
    category_dict = {}
    fd = file(dict_file)
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

def load_location_dict(tsv_file):

    nationality_list = [
        "壮族", "藏族", "裕固族", "彝族", "瑶族", "锡伯族", "乌孜别克族", "维吾尔族", "佤族", "土家族",
        "土族", "塔塔尔族", "塔吉克族", "水族", "畲族", "撒拉族", "羌族", "普米族", "怒族", "纳西族",
        "仫佬族", "苗族", "蒙古族", "门巴族", "毛南族", "满族", "珞巴族", "僳僳族", "黎族", "拉祜族",
        "柯尔克孜族", "景颇族", "京族", "基诺族", "回族", "赫哲族", "哈萨克族", "哈尼族", "仡佬族",
        "高山族", "鄂温克族", "俄罗斯族", "鄂伦春族", "独龙族", "东乡族", "侗族", "德昂族", "傣族",
        "达斡尔族", "朝鲜族", "布依族", "布朗族", "保安族", "白族", "阿昌族", "傈僳族", "汉族", "各族"
    ]
    nationality_list.sort(lambda x, y: cmp(len(x.decode("utf-8")), len(y.decode("utf-8"))), reverse=True)
    
    location_suffix_list = []
    for natitionality in nationality_list:
        location_suffix_list.append(natitionality)
        if len(natitionality.decode("utf-8")) > 2:
            location_suffix_list.append(natitionality[:-len("族")])
    location_suffix_list = product(location_suffix_list, ["自治区", "自治州", "自治县"])
    location_suffix_list = ["".join([a, b]) for a, b in location_suffix_list]
    location_suffix_list.extend(["土家族苗族自治县", "依族苗族自治县", "苗族瑶族傣族自治县", "布依族苗族自治州", "回族彝族自治县", "哈尼族彝族傣族自治县", "壮族瑶族自治县", "土家族苗族自治县", "黎族苗族自治县", "苗族侗族自治县", "满族蒙古族自治县", "拉祜族佤族布朗族傣族自治县", "苗族侗族自治州", "土家族苗族自治州", "彝族傣族自治县", "壮族苗族自治州", "黎族苗族自治县", "苗族布依族自治县", "仡佬族苗族自治县", "藏族羌族自治州", "布依族苗族自治州", "土家族苗族自治州", "回族土族自治县", "仡佬族苗族自治县", "彝族回族苗族自治县", "回族土族自治县", "彝族回族自治县", "土家族苗族自治县", "苗族土家族自治县", "蒙古族藏族自治州", "彝族苗族自治县", "保安族东乡族撒拉族自治县", "傣族景颇族自治州", "傣族佤族自治县", "布依族苗族自治县", "哈尼族彝族自治州"])
    location_suffix_list.extend(["特别行政区", "省", "市", "县", "区", "镇", "乡", "村"])
    location_suffix_list.sort(lambda x, y: cmp(len(x.decode("utf-8")), len(y.decode("utf-8"))), reverse=True)

    location_list = []
    fd = file(tsv_file)
    for row in fd:
        splited_row = row.strip().split()
        assert len(splited_row) == 3
        location_level, location_string, location_dir = splited_row
        location_dir = location_dir.split("_")
        location_list.append([location_level, location_string, location_dir])
    location_dict = dict((location_list[i][1], i) for i in xrange(len(location_list)))
    synonymy_map = {}
    for location_string in location_dict:
        synonymy_map[location_string] = location_string
        for location_suffix in location_suffix_list:
            if location_string.endswith(location_suffix):
                location_synonymy = location_string[:-len(location_suffix)]
                if len(location_synonymy.decode("utf-8")) < 2:
                    break
                if location_synonymy in synonymy_map and location_list[location_dict[synonymy_map[location_synonymy]]][0] >= location_list[location_dict[synonymy_map[location_string]]][0]:
                    break
                synonymy_map[location_synonymy] = location_string
                break
    #for location in synonymy_map:
    #    if location != synonymy_map[location]:
    #        print "%s\t->\t%s" % (location, synonymy_map[location])
    return location_dict, location_list, synonymy_map

def reduce_set(location_set, location_dict, location_list, synonymy_map):

    res_set = set([])
    location_set = set(synonymy_map[location_string] for location_string in location_set)
    for source_string in location_set:
        should_pass = False
        for target_string in location_set:
            if source_string == target_string:
                continue
            for target_parent_location in location_list[location_dict[target_string]][2]:
                if source_string == target_parent_location:
                    should_pass = True
                    break
            if should_pass:
                break
        if not should_pass:
            res_set.add(synonymy_map[source_string])
    return res_set

def location_judge_relation(query_location_set, bidword_location_set, location_dict, location_list, synonymy_map):

    query_location_set = reduce_set(set(synonymy_map[location_string] for location_string in query_location_set), location_dict, location_list, synonymy_map)
    bidword_location_set = reduce_set(set(synonymy_map[location_string] for location_string in bidword_location_set), location_dict, location_list, synonymy_map)

    for query_location in query_location_set:
        found_parent_flag = False
        for bidword_location in bidword_location_set:
            if query_location == bidword_location:
                found_parent_flag = True
                break
            if synonymy_map[bidword_location] in set(location_list[location_dict[synonymy_map[query_location]]][2]):
                found_parent_flag = True
                break
        if not found_parent_flag:
            return False
        #if found_parent_flag:
        #    return True
    return True
    #return False

def load_school_dict(tsv_file):

    school_dict = {}
    fd = file(tsv_file)
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

def school_judge_relation(query_school_set, bidword_school_set, synonymy_map):

    source_set = set()
    for school in query_school_set:
        source_set.add(synonymy_map[school])
        
    target_set = set()
    for school in bidword_school_set:
        target_set.add(synonymy_map[school])

    return source_set.issubset(target_set)

def stock_judge_relation(query_school_set, bidword_school_set, synonymy_map):

    source_set = set()
    for school in query_school_set:
        source_set.add(synonymy_map[school])
        
    target_set = set()
    for school in bidword_school_set:
        target_set.add(synonymy_map[school])

    return source_set.issubset(target_set)
    
def load_stock_dict(stock_file):

    stock_dict = {}
    code_dict = {}
    prefix_dict = {} # {A: [((A, B, C), 10010]), ((A, D, E), 10011)]}
    fd = file(stock_file)
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

def brand_exclusion(brand_set, category_dict, query, bidword_list):

    res_list = []
    exc_list = []
    
    query_brand_set = set()
    query_category_set = set()
    for query_seg in query.split():
        if query_seg in category_dict:
            query_brand_set.add(query_seg)
            query_category_set |= category_dict[query_seg]

    for bidword, score in bidword_list:
        if len(set(bidword_seg for bidword_seg in bidword.split() if bidword_seg in category_dict) & query_brand_set) > 0:
            res_list.append((bidword, score))
            continue
        is_exclusive = False
        for bidword_seg in bidword.split():
            if bidword_seg in category_dict:
                if len(category_dict[bidword_seg] & query_category_set) > 0:
                    is_exclusive = True
                    exc_list.append((bidword, score))
                    break
        if not is_exclusive:
            res_list.append((bidword, score))
    return res_list, exc_list

def location_exclusion(location_dict, location_list, location_synonymy_map, location_set, query, bidword_list):

    res_list = []
    exc_list = []
    
    query_location_set = set()
    for query_seg in query.split():
        if query_seg in location_set:
            query_location_set.add(query_seg)

    if len(query_location_set) == 0:
        res_list = bidword_list
        return res_list, exc_list

    for bidword, score in bidword_list:
        bidword_location_set = set()
        for bidword_seg in bidword.split():
            if bidword_seg in location_set:
                bidword_location_set.add(bidword_seg)
        if len(bidword_location_set) == 0:
            res_list.append((bidword, score))
            continue
        if location_judge_relation(query_location_set, bidword_location_set, location_dict, location_list, location_synonymy_map):
            res_list.append((bidword, score))
        else:
            exc_list.append((bidword, score))

    return res_list, exc_list

def school_exclusion(school_synonymy_map, query, bidword_list):

    res_list = []
    exc_list = []
    
    query_school_set = set()
    for query_seg in query.split():
        if query_seg in school_synonymy_map:
            query_school_set.add(query_seg)

    if len(query_school_set) == 0:
        res_list = bidword_list
        return res_list, exc_list

    for bidword, score in bidword_list:
        bidword_school_set = set()
        for bidword_seg in bidword.split():
            if bidword_seg in school_synonymy_map:
                bidword_school_set.add(bidword_seg)
        if len(bidword_school_set) == 0:
            res_list.append((bidword, score))
            continue
        if school_judge_relation(query_school_set, bidword_school_set, school_synonymy_map):
            res_list.append((bidword, score))
        else:
            exc_list.append((bidword, score))

    return res_list, exc_list

def coincide_exclusion(query, bidword_list):

    res_list = []
    exc_list = []

    query_term_set = set(query.split())
    query_length = sum([len(term) for term in query_term_set])
    if query_length == 0:
        exc_list = bidword_list
        res_list = []
        return res_list, exc_list
    for bidword, score in bidword_list:
        bidword_term_set = set(bidword.split())
        bidword_length = sum([len(term) for term in bidword_term_set])
        if bidword_length == 0:
            exc_list.append((bidword, score))
            continue
        intersection_set = query_term_set & bidword_term_set
        intersection_length = sum([len(term) for term in intersection_set])
        count_intersection_rate = float(len(intersection_set)) / min(float(len(query_term_set)), float(len(bidword_term_set)))
        length_intersection_rate = float(intersection_length) / min(float(query_length), float(bidword_length))
        if count_intersection_rate >= 0.6 or length_intersection_rate >= 0.6:
            exc_list.append((bidword, score))
        else:
            res_list.append((bidword, score))
        
    return res_list, exc_list

def stock_replace(code_dict, stock_dict, prefix_dict, query, bidword_list):

    res_list = []
    
    query_code_set = parse_code_set(code_dict, prefix_dict, query)
    if len(query_code_set) == 0:
        res_list = bidword_list
        return res_list

    res_set = set([])
    for bidword, score in bidword_list:
        assert score.replace('.', '').isdigit()
        new_bidword = replace_stock(code_dict, stock_dict, prefix_dict, query_code_set, bidword)
        if new_bidword not in res_set:
            res_list.append((new_bidword, score))
            res_set.add(new_bidword)
    return res_list
    
def main():

    #parser = ArgumentParser()
    #parser.add_argument("brand_dict_file", help = "category-brand file in space splited file format")
    #parser.add_argument("location_dict_file", help = "hierarchy location relation file in csv format")
    #parser.add_argument("school_dict_file", help = "china school file with its synonymy in tsv format")
    #parser.add_argument("stock_dict_file", help = "code-stock-seg file in tsv format")
    #args = parser.parse_args()
    #
    #brand_dict_file = args.brand_dict_file
    #location_dict_file = args.location_dict_file
    #school_dict_file = args.school_dict_file
    #stock_dict_file = args.stock_dict_file

    brand_dict_file = argv[1]
    location_dict_file = argv[2]
    school_dict_file = argv[3]
    stock_dict_file = argv[4]

    brand_set, category_dict = load_brand_dict(brand_dict_file)
    location_dict, location_list, location_synonymy_map = load_location_dict(location_dict_file)
    school_set, school_synonymy_map = load_school_dict(school_dict_file)
    code_dict, stock_dict, prefix_dict = load_stock_dict(stock_dict_file)

    # check location dict data
    location_set = set(location_synonymy_map)
    for location in location_list:
        assert location[1] in location_dict
    assert location_judge_relation(set(["黑龙江", "哈尔滨"]), set(["沈阳", "辽宁"]), location_dict, location_list, location_synonymy_map) is False
    assert location_judge_relation(set(["黑龙江", "哈尔滨", "沈阳"]), set(["哈尔滨", "沈阳"]), location_dict, location_list, location_synonymy_map) is True
    assert location_judge_relation(set(["黑龙江", "哈尔滨", "沈阳"]), set(["哈尔滨"]), location_dict, location_list, location_synonymy_map) is False
    assert location_judge_relation(set(["哈尔滨"]), set(["黑龙江"]), location_dict, location_list, location_synonymy_map) is True
    assert location_judge_relation(set(["沈阳"]), set(["沈阳"]), location_dict, location_list, location_synonymy_map) is True
    assert location_judge_relation(set(["沈阳"]), set(["吉林"]), location_dict, location_list, location_synonymy_map) is False
    assert location_judge_relation(set(["吉林市"]), set(["吉林省"]), location_dict, location_list, location_synonymy_map) is True
    assert location_judge_relation(set(["吉林省"]), set(["吉林市"]), location_dict, location_list, location_synonymy_map) is False
    assert location_judge_relation(set(["广州", "南宁"]), set(["南宁", "北京"]), location_dict, location_list, location_synonymy_map) is False
    assert location_judge_relation(set(["北京", "汉口"]), set(["北京", "青岛"]), location_dict, location_list, location_synonymy_map) is False
    assert location_judge_relation(set(["诸暨"]), set(["诸暨"]), location_dict, location_list, location_synonymy_map) is True
    assert location_judge_relation(set(["哈尔滨"]), set(["黑龙江"]), location_dict, location_list, location_synonymy_map) is True

    # check school dict data
    for school in school_set:
        assert school in school_synonymy_map

    # check stock dict data
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
    
    spliter = compile("(?<=\/[0-9].[0-9][0-9][0-9][0-9][0-9][0-9]) ")
    for line in stdin:
        splited_line = line.strip().split("\t")
        if len(splited_line) < 2:
            continue
        
        query = splited_line.pop(0)
        bidword_list = [('/'.join(bidword.split('/')[:-1]), bidword.split('/')[-1]) for bidword in spliter.split(splited_line.pop(-1))]

        res_list, exc_list = brand_exclusion(brand_set, category_dict, query, bidword_list)
        assert len(res_list) + len(exc_list) == len(bidword_list)
        
        bidword_list = res_list
        
        res_list, exc_list = location_exclusion(location_dict, location_list, location_synonymy_map, location_set, query, bidword_list)
        assert len(res_list) + len(exc_list) == len(bidword_list)
        
        bidword_list = res_list
        
        res_list, exc_list = school_exclusion(school_synonymy_map, query, bidword_list)
        assert len(res_list) + len(exc_list) == len(bidword_list)
        
        bidword_list = res_list
        
        res_list, exc_list = coincide_exclusion(query, bidword_list)
        assert len(res_list) + len(exc_list) == len(bidword_list)
        
        bidword_list = res_list

        res_list = stock_replace(code_dict, stock_dict, prefix_dict, query, bidword_list)
        
        bidword_list = res_list

        if DEBUG_FLAG:
            if len(exc_list) > 0:
                print "%s\t%s" % (query, ";".join(["%s%s" % (bidword, score) for bidword, score in exc_list]))
        else:
            if len(res_list) > 0:
                print "%s\t%s" % (query, ";".join(["%s%s" % (bidword, score) for bidword, score in res_list]))
    
if __name__ == "__main__":

    main()

