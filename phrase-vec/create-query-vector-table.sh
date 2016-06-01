#!/bin/bash
# 
# create-query-vector-table.sh
# Written by Jingwen HUANG <huangjingwen@360.cn>
# Generate query vector from query\t[seg^Cweight]* table.
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

query_vector_table="huangjingwen_query_vector"
query_weight_table="huangjingwen_query_weight"
word_vector_table="huangjingwen_word_vector"

alias shive='sudo -u hdp-guanggao -E /usr/bin/hadoop/software/hive//bin/hive'
shopt -s expand_aliases

echo "
create external table if not exists ${query_vector_table} (
query  string,
vector string
)
PARTITIONED BY (ds string)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
LINES TERMINATED BY '\n'
STORED AS TEXTFILE;
alter table ${query_vector_table} drop if exists partition(ds='${DATE}');

add file phrase-vector-stream.py;

from 
(
    from 
    (
        select t1.query, t1.word, t1.weight, t2.vector 
        from
        (
            select query, split(term, '\003')[0] as word, split(term, '\003')[1] as weight
            from
            (
                select query, term from ${query_weight_table} a lateral view explode(split(a.terms, '\002' )) b as term where ds = '${DATE}'
            )qt
        ) t1
        join
        (
            select word, vector from ${word_vector_table} where ds = '${DATE}'
        ) t2
        on
        (   
            t1.word = t2.word
        )
        distribute by t1.query sort by t1.query
    ) map_out
    reduce map_out.query, map_out.word,  map_out.weight, map_out.vector 
    using 'python phrase-vector-stream.py' as query, vector 
    ROW FORMAT DELIMITED
    FIELDS TERMINATED BY '\t'
) reduce_out 
insert overwrite table ${query_vector_table} partition(ds='$DATE') 
select query, vector;
exit;
" | shive > create-query-vector-table.log
