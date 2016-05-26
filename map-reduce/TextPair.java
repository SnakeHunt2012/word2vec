package com.qihu.rank.common;

/**
 * Created by nixingliang on 2015/12/2.
 */

import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.WritableComparable;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;

public class TextPair implements WritableComparable<TextPair> {
    private Text first;
    private Float second;

    public TextPair() {
        set(new Text(), 0F);
    }

    public TextPair(long first, Float second) {
        set(new Text(String.valueOf(first)), second);
    }

    public TextPair(String first, Float second) {
        set(new Text(first), second);
    }

    public TextPair(Text first, Float second) {
        set(first, second);
    }


    public void set(Text first, Float second) {
        this.first = first;
        this.second = second;
    }

    public Text getFirst() {
        return first;
    }

    public Float getSecond() {
        return second;
    }

    @Override
    public void write(DataOutput out) throws IOException {
        first.write(out);
        out.writeFloat(second);
    }

    @Override
    public void readFields(DataInput in) throws IOException {
        first.readFields(in);
        second = in.readFloat();
    }

    @Override
    public int hashCode() {
        return first.hashCode() * 31 + second.hashCode();
    }

    @Override
    public boolean equals(Object o) {
        if (o instanceof TextPair) {
            TextPair tp = (TextPair) o;
            return first.equals(tp.first) && second.equals(tp.second);
        }
        return false;
    }

    @Override
    public String toString() {
//        if (second.getLength() == 0)
//            return first.toString();
//        else
        return first + "\u0001" + second;
    }

    @Override
    public int compareTo(TextPair tp) {
        int cmp = first.compareTo(tp.first);
        if (cmp != 0) {
            return cmp;
        }
        return second.compareTo(tp.second);
    }
}