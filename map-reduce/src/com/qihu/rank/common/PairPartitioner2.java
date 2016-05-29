package com.qihu.rank.common;

/**
 * Created by nixingliang on 2015/12/2.
 */
import java.io.*;
import java.util.*;

import org.apache.hadoop.fs.*;
import org.apache.hadoop.conf.*;
import org.apache.hadoop.io.*;
import org.apache.hadoop.mapreduce.*;
import org.apache.hadoop.util.*;


public class PairPartitioner2<V> extends Partitioner<TextPair, V> {

    @Override
    public int getPartition(TextPair key, V value, int numPartitions) {
        return (key.getFirst().hashCode() & Integer.MAX_VALUE) % numPartitions;
    }

    public static class KeyComparator extends WritableComparator {
        protected KeyComparator() {
            super(TextPair.class, true);
        }
        @Override
        public int compare(WritableComparable w1, WritableComparable w2) {
            TextPair ip1 = (TextPair) w1;
            TextPair ip2 = (TextPair) w2;
            return ip1.compareTo(ip2);
        }
    }

    public static class GroupComparator extends WritableComparator {
        protected GroupComparator() {
            super(TextPair.class, true);
        }
        @Override
        public int compare(WritableComparable w1, WritableComparable w2) {
            TextPair ip1 = (TextPair) w1;
            TextPair ip2 = (TextPair) w2;
            return ip1.getFirst().compareTo(ip2.getFirst());
        }
    }
}