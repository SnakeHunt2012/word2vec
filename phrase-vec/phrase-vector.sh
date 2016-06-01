#!/bin/bash
# 
# phrase-vector.sh
# Written by Jingwen HUANG <huangjingwen@360.cn>
# Convert phrase (query/bidword) to vector.
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

bash create-query-vector-table.sh "${DATE}"
bash create-bidword-vector-table.sh "${DATE}"
