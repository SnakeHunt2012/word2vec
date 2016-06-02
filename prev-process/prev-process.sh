#!/bin/bash
# 
# prev-process.sh
# Written by Jingwen HUANG <SnakeHunt2012@gmail.com>
# Segment and trim query/bidword, then upload table huangjingwen_query/bidword_triple.
#

err_args=85

function usage ()
{
    echo "Usage: `basename $0` xxxx-xx-xx"
}

case "$1" in
    ""                    ) usage; exit ${err_args};;
    [0-9]*-[0-9]*-[0-9]*  ) DATE=$1;;
    *                     ) usage; exit ${err_args};;
esac

alias shadoop='sudo -E -u hdp-guanggao /usr/bin/hadoop/software/hadoop//bin/hadoop'
alias shive='sudo -u hdp-guanggao -E /usr/bin/hadoop/software/hive//bin/hive'
shopt -s expand_aliases

# download ori
shive -e "select distinct(query) from srp_query_pv where pv > 45 and ds='${DATE}';" > query-ori.tsv
shive -e "select distinct(bidword) from ad_bidword_pv_click where (click > 0 or pv > 20) and ds='2016-05-22';" > bidword-ori.tsv

# upload ori
shadoop fs -put query-ori.tsv "/home/hdp-guanggao/huangjingwen/data/query-ori/ds=${DATE}"
shadoop fs -put bidword-ori.tsv "/home/hdp-guanggao/huangjingwen/data/bidword-ori/ds=${DATE}"

# segment
bash segment.sh query "${DATE}"
bash segment.sh bidword "${DATE}"

# download seg
shadoop fs -cat "/home/hdp-guanggao/huangjingwen/data/query-seg/ds=${DATE}/part*" > query-seg.tsv
shadoop fs -cat "/home/hdp-guanggao/huangjingwen/data/bidword-seg/ds=${DATE}/part*" > bidword-seg.tsv

# clean (trim-suffix)
python trim-suffix.py --shrink stopword.tsv suffix-dict.tsv query-seg.tsv > query-clean.tsv
python trim-suffix.py --shrink stopword.tsv suffix-dict.tsv bidword-seg.tsv > bidword-clean.tsv

# upload to hdfs
shadoop fs -mkdir "/home/hdp-guanggao/huangjingwen/data/query-clean/ds=${DATE}"
shadoop fs -mkdir "/home/hdp-guanggao/huangjingwen/data/bidword-clean/ds=${DATE}"

shadoop fs -put "query-clean.tsv" "/home/hdp-guanggao/huangjingwen/data/query-clean/ds=${DATE}"
shadoop fs -put "bidword-clean.tsv" "/home/hdp-guanggao/huangjingwen/data/bidword-clean/ds=${DATE}"

# upload to hive
bash create-query-seg-table.sh "${DATE}"
bash create-bidword-seg-table.sh "${DATE}"
bash create-query-clean-table.sh "${DATE}"
bash create-bidword-clean-table.sh "${DATE}"
bash create-query-triple-table.sh "${DATE}"
bash create-bidword-triple-table.sh "${DATE}"
