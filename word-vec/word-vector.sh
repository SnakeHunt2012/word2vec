#!/bin/bash
# 
# word-vector.sh
# Written by Jingwen HUANG <huangjingwen@360.cn>
# Upload new word2vec data into table huangjingwen_word_vector
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

shadoop fs -mkdir "/home/hdp-guanggao/huangjingwen/data/word-vector/ds=${DATE}"
shadoop fs -put vectors.tsv "/home/hdp-guanggao/huangjingwen/data/word-vector/ds=${DATE}"

bash create-word-vector-table.sh "${DATE}"
