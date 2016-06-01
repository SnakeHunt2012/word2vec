#!/bin/bash
# 
# create-word-vector-table.sh
# Written by Jingwen HUANG <huangjingwen@360.cn>
# Upload word vectors from vectors.tsv in format word\tfloat float float ...
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

word_vector_table="huangjingwen_word_vector"

alias shive='sudo -u hdp-guanggao -E /usr/bin/hadoop/software/hive//bin/hive'
shopt -s expand_aliases

echo "
create external table if not exists ${word_vector_table} (
word  string,
vector string
)
PARTITIONED BY (ds string)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE;
alter table ${word_vector_table} drop if exists partition(ds='${DATE}');
alter table ${word_vector_table} add partition(ds='${DATE}') location '/home/hdp-guanggao/huangjingwen/data/word-vector/ds=${DATE}';
" | shive > create-word-vector-table.log
