#!/bin/bash
# 
# weight.sh
# Written by Jingwen HUANG <huangjingwen@360.cn>
# Patch weight into query/bidword-clean.tsv > query/bidword-weight.tsv
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

python patch-weight.py global-weight-query-bidword.tsv ../prev-process/query-clean.tsv > query-weight.tsv
python patch-weight.py global-weight-query-bidword.tsv ../prev-process/bidword-clean.tsv > bidword-weight.tsv

alias shadoop='sudo -E -u hdp-guanggao /usr/bin/hadoop/software/hadoop//bin/hadoop'
alias shive='sudo -u hdp-guanggao -E /usr/bin/hadoop/software/hive//bin/hive'
shopt -s expand_aliases

shadoop fs -mkdir "/home/hdp-guanggao/huangjingwen/data/query-weight/ds=${DATE}"
shadoop fs -mkdir "/home/hdp-guanggao/huangjingwen/data/bidword-weight/ds=${DATE}"

shadoop fs -put query-weight.tsv /home/hdp-guanggao/huangjingwen/data/query-weight/ds=${DATE}
shadoop fs -put bidword-weight.tsv /home/hdp-guanggao/huangjingwen/data/bidword-weight/ds=${DATE}

bash create-query-weight-table.sh "${DATE}"
bash create-bidword-weight-table.sh "${DATE}"
