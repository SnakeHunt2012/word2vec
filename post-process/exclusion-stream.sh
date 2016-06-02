#!/bin/bash
# 
# post-process.sh
# Written by Jingwen HUANG <SnakeHunt2012@gmail.com>
# Post-process of the query->bidword procedure.
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

INPUT=/home/hdp-guanggao/hive/warehouse/hdp_guanggao.db/w2v_query_bidword_sim_extension/ds=${DATE}
OUTPUT=/home/hdp-guanggao/huangjingwen/data/query-bidword-extension/raw

STREAMING=/usr/bin/hadoop/software/hadoop/contrib/streaming/hadoop-streaming.jar

alias shadoop='sudo -E -u hdp-guanggao /usr/bin/hadoop/software/hadoop//bin/hadoop'
shopt -s expand_aliases
shadoop fs -test -e $OUTPUT
if [ $? -eq 0 ]
then
    shadoop fs -rmr $OUTPUT
fi

shadoop jar $STREAMING \
-D mapred.linerecordreader.maxlength=1024000 \
-D mapred.job.priority=VERY_HIGH \
-D mapred.reduce.tasks=0 \
-D mapred.job.name='huangjingwen:query-bidword-exclusion' \
-D map.output.key.field.separator='\t' \
-D stream.num.map.output.key.fields=1 \
-inputformat org.apache.hadoop.mapred.lib.CombineTextInputFormat \
-input $INPUT \
-output $OUTPUT \
-mapper './anaconda/bin/python exclusion-stream.py category-brand.tsv china-higher-location.tsv school-with-synonym.tsv stock-seg-dict.tsv' \
-file exclusion-stream.py \
-file category-brand.tsv \
-file china-higher-location.tsv \
-file school-with-synonym.tsv \
-file stock-seg-dict.tsv \
-cacheArchive '/home/hdp-guanggao/huangjingwen/lib/anaconda.tar.gz#anaconda'        

