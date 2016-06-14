#!/bin/bash
# 
# tag.sh
# Written by Jingwen HUANG <SnakeHunt2012@gmail.com>
# Parsing tagging from query/bidword_seg.
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

g++ tag.cc -o tag -l postagger -l parser
chmod +x tag

STREAMING=/usr/bin/hadoop/software/hadoop/contrib/streaming/hadoop-streaming.jar

alias shadoop='sudo -E -u hdp-guanggao /usr/bin/hadoop/software/hadoop//bin/hadoop'
shopt -s expand_aliases

INPUT=/home/hdp-guanggao/huangjingwen/data/query-seg/ds=${DATE}
OUTPUT=/home/hdp-guanggao/huangjingwen/data/query-tag/ds=${DATE}

shadoop fs -test -e $OUTPUT
if [ $? -eq 0 ]
then
    shadoop fs -rmr $OUTPUT
fi

shadoop jar $STREAMING \
-D mapred.linerecordreader.maxlength=1024000 \
-D mapred.job.priority=VERY_HIGH \
-D mapred.reduce.tasks=0 \
-D mapred.job.name='huangjingwen:query-tag' \
-D map.output.key.field.separator='\t' \
-D stream.num.map.output.key.fields=1 \
-inputformat org.apache.hadoop.mapred.lib.CombineTextInputFormat \
-input $INPUT \
-output $OUTPUT \
-mapper 'bash tag-stream.sh' \
-file tag-stream.sh \
-file tag \
-cacheArchive '/home/hdp-guanggao/huangjingwen/lib/ltp.tar.gz#ltp'

#INPUT=/home/hdp-guanggao/huangjingwen/data/bidword-seg/ds=${DATE}
#OUTPUT=/home/hdp-guanggao/huangjingwen/data/bidword-tag/ds=${DATE}
#
#shadoop fs -test -e $OUTPUT
#if [ $? -eq 0 ]
#then
#    shadoop fs -rmr $OUTPUT
#fi
#
#shadoop jar $STREAMING \
#-D mapred.linerecordreader.maxlength=1024000 \
#-D mapred.job.priority=VERY_HIGH \
#-D mapred.reduce.tasks=0 \
#-D mapred.job.name='huangjingwen:bidword-tag' \
#-D map.output.key.field.separator='\t' \
#-D stream.num.map.output.key.fields=1 \
#-inputformat org.apache.hadoop.mapred.lib.CombineTextInputFormat \
#-input $INPUT \
#-output $OUTPUT \
#-mapper './tag pos.model parser.model' \
#-file tag-stream.sh \
#-file tag \
#-cacheArchive '/home/hdp-guanggao/huangjingwen/lib/model.tar.gz#model'

