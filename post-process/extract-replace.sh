#!/bin/bash

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

INPUT="/home/hdp-guanggao/huangjingwen/data/query-bidword-extension/raw"
OUTPUT="/home/hdp-guanggao/huangjingwen/data/replace-record/ds=${DATE}"

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
-mapper './anaconda/bin/python extract-replace.py' \
-file extract-replace.py \
-cacheArchive '/home/hdp-guanggao/huangjingwen/lib/anaconda.tar.gz#anaconda'        
