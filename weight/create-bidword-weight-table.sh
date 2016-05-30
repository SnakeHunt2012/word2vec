#!/bin/bash
# 
# create-bidword-weight-table.sh
# Written by Jingwen HUANG <huangjingwen@360.cn>
# Upload bidword weight from bidword-weight.tsv in format bidword\tterm^Bweight^Aterm^Bweight ...
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

bidword_weight_table="huangjingwen_bidword_weight"

alias shive='sudo -u hdp-guanggao -E /usr/bin/hadoop/software/hive//bin/hive'
shopt -s expand_aliases

echo "
create external table if not exists ${bidword_weight_table} (
bidword string,
terms string
)
PARTITIONED BY (ds string)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE;

alter table ${bidword_weight_table} drop if exists partition(ds='${DATE}');
alter table ${bidword_weight_table} add partition(ds='${DATE}') location '/home/hdp-guanggao/huangjingwen/data/bidword-weight/ds=${DATE}';
" | shive > create-bidword-weight-table.log
