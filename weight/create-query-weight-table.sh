#!/bin/bash
# 
# create-query-weight-table.sh
# Written by Jingwen HUANG <SnakeHunt2012@gmail.com>
# Upload query weight from query-weight.tsv in format query\tterm^Bweight^Aterm^Bweight ...
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

query_weight_table="huangjingwen_query_weight"

alias shive='sudo -u hdp-guanggao -E /usr/bin/hadoop/software/hive//bin/hive'
shopt -s expand_aliases

echo "
create external table if not exists ${query_weight_table} (
query string,
terms string
)
PARTITIONED BY (ds string)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE;

alter table ${query_weight_table} drop if exists partition(ds='${DATE}');
alter table ${query_weight_table} add partition(ds='${DATE}') location '/home/hdp-guanggao/huangjingwen/data/query-weight/ds=${DATE}';
" | shive > create-query-weight-table.log
