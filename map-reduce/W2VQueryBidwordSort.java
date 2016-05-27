package com.qihu.match;

import com.qihu.rank.common.Common;
import com.qihu.rank.common.PairPartitioner2;
import com.qihu.rank.common.TextPair;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.conf.Configured;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.compress.CompressionCodec;
import org.apache.hadoop.io.compress.GzipCodec;
import org.apache.hadoop.mapred.JobPriority;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.MultipleInputs;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextMultiOutputFormat;
import org.apache.hadoop.util.Tool;
import org.apache.hadoop.util.ToolRunner;

import java.io.IOException;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.PriorityQueue;

public class W2VQueryBidwordSort extends Configured implements Tool {


    public static void main(String[] args) throws Exception {
        int exitCode = ToolRunner.run(new Configuration(), new W2VQueryBidwordSort(), args);
        System.exit(exitCode);
    }

    public static Job configJob(Configuration contextConf) throws IOException, URISyntaxException {
//        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
//        String date_str = sdf.format(cal.getTime());

        // JOB INIT
        Job job = new Job(contextConf);
        job.setJarByClass(W2VQueryBidwordSort.class);
        job.setJobName("nixingliang_w2v_query_bidword_sort");

        // INPUT PATH
        String queryDir = "/home/hdp-guanggao/huangjingwen/data/query-norm-vector/ds=2016-05-24";
        String bidwordDir = "/home/hdp-guanggao/huangjingwen/data/bidword-norm-vector/ds=2016-05-24";
        Path queryPath = new Path(queryDir + "/*");
        Path bidwordPath = new Path(bidwordDir + "/*");
        MultipleInputs.addInputPath(job, queryPath, TextInputFormat.class, QueryMap.class);
        MultipleInputs.addInputPath(job, bidwordPath, TextInputFormat.class, BidwordMap.class);

        // OUTPUT PATH
        String output = "/home/hdp-guanggao/huangjingwen/data/query-bidword-candidate/ds=2016-05-24";
        Path outPath = new Path(output);
        FileOutputFormat.setOutputPath(job, outPath);
        FileSystem fs = FileSystem.get(job.getConfiguration());
        fs.delete(outPath, true);

        // FORMAT
        job.setMapOutputKeyClass(TextPair.class);
        job.setMapOutputValueClass(Text.class);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);

        // MR RUN
        job.setReducerClass(Reduce.class);
        job.setNumReduceTasks(1000);
        job.setPartitionerClass(PairPartitioner2.class);
        job.setSortComparatorClass(PairPartitioner2.KeyComparator.class);
        job.setGroupingComparatorClass(PairPartitioner2.GroupComparator.class);

        // ALMOST NEVER CHANGE
        job.getConfiguration().set("mapreduce.user.classpath.first", "true");
        job.getConfiguration().setBoolean("mapred.output.compress", true);
        job.getConfiguration().setClass("mapred.output.compression.codec", GzipCodec.class, CompressionCodec.class);
        job.getConfiguration().setLong("mapred.job.max.map.running", 4000);
        job.getConfiguration().setLong("mapred.job.max.reduce.running", 1000);
        job.getConfiguration().set("mapred.job.priority", JobPriority.NORMAL.name());
        job.getConfiguration().setLong("mapred.max.split.size", 32 * 1024 * 1024);
        job.getConfiguration().setLong("mapred.min.split.size", 32 * 1024 * 1024);
        job.getConfiguration().setLong("mapred.reduce.max.size.per.file", 32 * 1024 * 1024);
        job.setOutputFormatClass(TextMultiOutputFormat.class);

        return job;
    }

    public static Job configJob2(Configuration contextConf) throws IOException, URISyntaxException {
//        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
//        String date_str = sdf.format(cal.getTime());

        // JOB INIT
        Job job = new Job(contextConf);
        job.setJarByClass(W2VQueryBidwordSort.class);
        job.setJobName("nixingliang_w2v_query_bidword_sort2");

        // INPUT PATH
        String queryDir = "/home/hdp-guanggao/huangjingwen/data/query-bidword-candidate/ds=2016-05-24";
        Path queryPath = new Path(queryDir + "/*");
        MultipleInputs.addInputPath(job, queryPath, TextInputFormat.class, Map2.class);


        // OUTPUT PATH
        String output = "/home/hdp-guanggao/huangjingwen/data/query-bidword/ds=2016-05-24";
        Path outPath = new Path(output);
        FileOutputFormat.setOutputPath(job, outPath);
        FileSystem fs = FileSystem.get(job.getConfiguration());
        fs.delete(outPath, true);

        // FORMAT
        job.setMapOutputKeyClass(Text.class);
        job.setMapOutputValueClass(Text.class);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);

        // MR RUN
        job.setReducerClass(Reduce2.class);
        job.setNumReduceTasks(1000);


        // ALMOST NEVER CHANGE
        job.getConfiguration().set("mapreduce.user.classpath.first", "true");
        job.getConfiguration().setBoolean("mapred.output.compress", true);
        job.getConfiguration().setClass("mapred.output.compression.codec", GzipCodec.class, CompressionCodec.class);
        job.getConfiguration().setLong("mapred.job.max.map.running", 4000);
        job.getConfiguration().setLong("mapred.job.max.reduce.running", 1000);
        job.getConfiguration().set("mapred.job.priority", JobPriority.NORMAL.name());
        job.getConfiguration().setLong("mapred.max.split.size", 128 * 1024 * 1024);
        job.getConfiguration().setLong("mapred.min.split.size", 128 * 1024 * 1024);
        job.getConfiguration().setLong("mapred.reduce.max.size.per.file", 128 * 1024 * 1024);
        job.setOutputFormatClass(TextMultiOutputFormat.class);

        return job;
    }

    @Override
    public int run(String[] args) throws Exception {
        Configuration conf = getConf();
        Job job = configJob(conf);
        if (!job.waitForCompletion(true))
            return -1;

        job = configJob2(conf);
        if (!job.waitForCompletion(true))
            return -1;

        return 0;
    }

    enum Counters {
        BIDWORD_ERROR, BIDWORD_VECTOR_ERROR, QUERY_HASH_COUNT, BIDWORD_COUNT,
        QUERY_ERROR, QUERY_VECTOR_ERROR, QUERY_COUNT
    }


    public static class BidwordMap extends Mapper<LongWritable, Text, TextPair, Text> {

        @Override
        public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {

            String line = value.toString();
            String[] fields = line.split("\t", -1);
            if (fields.length != 2) {
                context.getCounter(Counters.BIDWORD_ERROR).increment(1);
                return;
            }

            fields = fields[1].split(" ", -1);
            if (fields.length != 200) {
                context.getCounter(Counters.BIDWORD_VECTOR_ERROR).increment(1);
                return;
            }

            float[] feature = new float[200];
            for (int i = 0; i < 200; i++) {
                feature[i] = Float.parseFloat(fields[i]);
            }

            int hashId = Common.getLSH(feature);

            context.write(new TextPair(hashId, 0F), new Text("0\t" + line));
            context.getCounter(Counters.BIDWORD_COUNT).increment(1);


        }
    }

    public static class QueryMap extends Mapper<LongWritable, Text, TextPair, Text> {

        @Override
        public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {
            String line = value.toString();
            String[] fields = line.split("\t", -1);
            if (fields.length != 2) {
                context.getCounter(Counters.QUERY_ERROR).increment(1);
                return;
            }

            fields = fields[1].split(" ", -1);
            if (fields.length != 200) {
                context.getCounter(Counters.QUERY_VECTOR_ERROR).increment(1);
                return;
            }

            float[] feature = new float[200];
            for (int i = 0; i < 200; i++) {
                feature[i] = Float.parseFloat(fields[i]);
            }

            HashSet<Integer> hashIds = Common.getLSHList(feature);

            for (int i : hashIds) {
                context.write(new TextPair(i, 1F), new Text("1\t" + line));
                context.getCounter(Counters.QUERY_HASH_COUNT).increment(1);
            }
            context.getCounter(Counters.QUERY_COUNT).increment(1);
        }
    }

    public static class Reduce extends Reducer<TextPair, Text, Text, Text> {

        @Override
        public void reduce(TextPair key, Iterable<Text> values, Context context) throws IOException, InterruptedException {

            ArrayList<String> bidwords = new ArrayList<String>();
            ArrayList<float[]> vectors = new ArrayList<float[]>();
            // remove vector-nomalization logic
            //ArrayList<Float> bidwordNorms = new ArrayList<Float>();
            boolean printed = false;
            int maxBidwordCount = 500;

            PriorityQueue<TextPair> bid2sim = new PriorityQueue<TextPair>(maxBidwordCount, new Comparator<TextPair>() {
                @Override
                public int compare(TextPair o1, TextPair o2) {

                    float weight1 = o1.getSecond();
                    float weight2 = o2.getSecond();

                    if (weight1 < weight2) {
                        return -1;
                    } else if (weight1 > weight2) {
                        return 1;
                    } else {
                        return 0;
                    }
                }
            });

            for (Text value : values) {
                String[] fields = value.toString().split("\t", -1);
                if (fields[0].equals("0")) {
                    String bidword = fields[1];

                    fields = fields[2].split(" ", -1);
                    if (fields.length != 200) {
                        context.getCounter(Counters.BIDWORD_VECTOR_ERROR).increment(1);
                        continue;
                    }

                    float[] feature = new float[200];
                    for (int i = 0; i < 200; i++) {
                        feature[i] = Float.parseFloat(fields[i]);
                    }

                    // remove vector-nomalization logic 
                    //float bidwordNorm = (float) Math.sqrt(Common.getInnerProduct(feature, feature));

                    bidwords.add(bidword);
                    vectors.add(feature);
                    // remove vector-nomalization logic 
                    //bidwordNorms.add(bidwordNorm);
                } else {
                    if (!printed) {
                        System.out.println(bidwords.size());
                        printed = true;
                    }

                    String query = fields[1];

                    fields = fields[2].split(" ", -1);
                    if (fields.length != 200) {
                        context.getCounter(Counters.QUERY_VECTOR_ERROR).increment(1);
                        continue;
                    }

                    float[] feature = new float[200];
                    for (int i = 0; i < 200; i++) {
                        feature[i] = Float.parseFloat(fields[i]);
                    }

                    // remove vector-nomalization logic
                    //double queryNorm = Math.sqrt(Common.getInnerProduct(feature, feature));
                    for (int i = 0; i < bidwords.size(); ++i) {
                        // remove vector-nomalization logic
                        //float similarity = (float) (Common.getInnerProduct(feature, vectors.get(i)) / (queryNorm * bidwordNorms.get(i)));
                        float similarity = (float) (Common.getInnerProduct(feature, vectors.get(i)));

                        if (similarity < 0.5) {
                            continue;
                        }

                        bid2sim.add(new TextPair(bidwords.get(i), similarity));
                        
                        if (bid2sim.size() > maxBidwordCount) {
                            bid2sim.poll();
                        }
                    }

                    StringBuilder sb = new StringBuilder();
                    sb.append(query).append(Common.CTRL_A);

                    while (!bid2sim.isEmpty()) {
                        TextPair temp = bid2sim.poll();
                        sb.append(temp.getFirst()).append(Common.CTRL_C).append(temp.getSecond()).append(Common.CTRL_B);
                    }

                    context.write(new Text(sb.substring(0, sb.length() - 1)), null);
                    context.getCounter(Counters.QUERY_COUNT).increment(1);
                }
            }
        }
    }


    public static class Map2 extends Mapper<LongWritable, Text, Text, Text> {

        @Override
        public void map(LongWritable key, Text value, Context context) throws IOException, InterruptedException {

            String[] fields = value.toString().split(Common.CTRL_A, -1);
            if (fields.length != 2) {
                context.getCounter(Counters.QUERY_ERROR).increment(1);
                return;
            }

            context.write(new Text(fields[0]), new Text(fields[1]));
            context.getCounter(Counters.QUERY_COUNT).increment(1);
        }
    }

    public static class Reduce2 extends Reducer<Text, Text, Text, Text> {

        @Override
        public void reduce(Text key, Iterable<Text> values, Context context) throws IOException, InterruptedException {

            String query = key.toString();
            int maxBidwordCount = 1000;

            PriorityQueue<TextPair> bid2sim = new PriorityQueue<TextPair>(maxBidwordCount, new Comparator<TextPair>() {
                @Override
                public int compare(TextPair o1, TextPair o2) {

                    float weight1 = o1.getSecond();
                    float weight2 = o2.getSecond();

                    if (weight1 < weight2) {
                        return -1;
                    } else if (weight1 > weight2) {
                        return 1;
                    } else {
                        return 0;
                    }
                }
            });

            for (Text value : values) {
                String[] fields = value.toString().split(Common.CTRL_B, -1);

                for (String s : fields) {
                    String[] elements = s.split(Common.CTRL_C, -1);
                    bid2sim.add(new TextPair(elements[0], Float.parseFloat(elements[1])));

                    if (bid2sim.size() > maxBidwordCount) {
                        bid2sim.poll();
                    }
                }
            }
            
            StringBuilder sb = new StringBuilder();
            sb.append(query).append(Common.CTRL_A);
            
            while (!bid2sim.isEmpty()) {
                TextPair temp = bid2sim.poll();
                sb.append(temp.getFirst()).append(Common.CTRL_C).append(temp.getSecond()).append(Common.CTRL_B);
            }
            
            context.write(new Text(sb.substring(0, sb.length() - 1)), null);
            context.getCounter(Counters.QUERY_COUNT).increment(1);
        }
    }
}
