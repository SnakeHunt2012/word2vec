#!/bin/bash

INPUT=/home/hdp-guanggao/huangjingwen/input
OUTPUT=/home/hdp-guanggao/huangjingwen/output
STREAMING=/usr/bin/hadoop/software/hadoop/contrib/streaming/hadoop-streaming.jar

alias shadoop='sudo -E -u hdp-guanggao /usr/bin/hadoop/software/hadoop//bin/hadoop'
shopt -s expand_aliases

shadoop jar $STREAMING \
-D mapred.linerecordreader.maxlength=1024000 \
-D mapred.reduce.tasks=500 \
-D mapred.job.priority=VERY_HIGH \
-D mapred.job.name='huangjingwen:pure-not-match' \
-D map.output.key.field.separator='\t' \
-D stream.num.map.output.key.fields=1 \
-inputformat org.apache.hadoop.mapred.lib.CombineTextInputFormat \
-input $INPUT \
-output $OUTPUT \
-mapper 'python pure-not-match-stream.py' \
-file pure-not-match-stream.py 



