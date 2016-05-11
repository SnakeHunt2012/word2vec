#!/usr/bin/env python
# -*- coding: utf-8 -*-

from re import compile
from time import time
from codecs import open
from argparse import ArgumentParser
from itertools import combinations, product

DEBUG_FLAG = False

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

def duration(start, end):

    second = (end - start) % 60
    minute = (end - start) % 3600 / 60
    hour = (end - start) / 3600
    return "%d:%02d:%02d" % (hour, minute, second)

def load_dict(tsv_file):

    location_list = []
    with open(tsv_file, 'r') as fd:
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

def judge_relation(query_location_set, bidword_location_set, location_dict, location_list, synonymy_map):

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
    return True

def main():

    parser = ArgumentParser()
    parser.add_argument("tsv_file", help = "hierarchy location relation file in csv format")
    parser.add_argument("sim_file", help = "query to bid sim file in tsv format")
    args = parser.parse_args()

    tsv_file = args.tsv_file
    sim_file = args.sim_file

    start_time = time()
    location_dict, location_list, synonymy_map = load_dict(tsv_file) # 0:location_level 1:location_string 2:location_dir
    end_time = time()

    location_set = set(synonymy_map)

    for location in location_list:
        assert location[1] in location_dict

    assert judge_relation(set(["黑龙江", "哈尔滨"]), set(["沈阳", "辽宁"]), location_dict, location_list, synonymy_map) is False
    assert judge_relation(set(["黑龙江", "哈尔滨", "沈阳"]), set(["哈尔滨", "沈阳"]), location_dict, location_list, synonymy_map) is True
    assert judge_relation(set(["黑龙江", "哈尔滨", "沈阳"]), set(["哈尔滨"]), location_dict, location_list, synonymy_map) is False
    assert judge_relation(set(["哈尔滨"]), set(["黑龙江"]), location_dict, location_list, synonymy_map) is True
    assert judge_relation(set(["沈阳"]), set(["沈阳"]), location_dict, location_list, synonymy_map) is True
    assert judge_relation(set(["沈阳"]), set(["吉林"]), location_dict, location_list, synonymy_map) is False
    assert judge_relation(set(["吉林市"]), set(["吉林省"]), location_dict, location_list, synonymy_map) is True
    assert judge_relation(set(["吉林省"]), set(["吉林市"]), location_dict, location_list, synonymy_map) is False
    assert judge_relation(set(["广州", "南宁"]), set(["南宁", "北京"]), location_dict, location_list, synonymy_map) is False
    assert judge_relation(set(["北京", "汉口"]), set(["北京", "青岛"]), location_dict, location_list, synonymy_map) is False

    spliter = compile("(?<=\/[0-9].[0-9][0-9][0-9][0-9][0-9][0-9]) ")
    with open(sim_file, 'r') as fd:
        for line in fd:
            splited_line = line.strip().split("\t")
            if len(splited_line) < 2:
                continue
            
            query = splited_line.pop(0)
            #bidword_list = "".join(splited_line).strip(";").split(";")
            bidword_list = [('/'.join(bidword.split('/')[:-1]), bidword.split('/')[-1]) for bidword in spliter.split(splited_line.pop(-1))]
        
            query_location_set = set()
            for query_seg in query.split():
                if query_seg in location_set:
                    query_location_set.add(query_seg)

            if len(query_location_set) == 0:
                if not DEBUG_FLAG:
                    print "%s\t%s" % (query, " ".join(["%s/%s" % (bidword, score) for bidword, score in bidword_list]))
                continue
        
            res_list = []
            exc_list = [] # for debug
            for bidword, score in bidword_list:
                bidword_location_set = set()
                for bidword_seg in bidword.split():
                    if bidword_seg in location_set:
                        bidword_location_set.add(bidword_seg)
                if len(bidword_location_set) == 0:
                    res_list.append("%s/%s" % (bidword, score))
                    continue
                if judge_relation(query_location_set, bidword_location_set, location_dict, location_list, synonymy_map):
                    res_list.append("%s/%s" % (bidword, score))
                else:
                    exc_list.append("%s/%s" % (bidword, score))
            assert len(res_list) + len(exc_list) == len(bidword_list)

            if DEBUG_FLAG:
                if len(exc_list) > 0:
                    print "%s\t%s" % (query, " ".join(exc_list))
            else:
                if len(res_list) > 0:
                    print "%s\t%s" % (query, " ".join(res_list))
                
if __name__ == "__main__":

    main()

