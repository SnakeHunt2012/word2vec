#!/usr/bin/env python
# -*- coding: utf-8

from threading import Thread
from codecs import open
from json import loads
from numpy import zeros
from argparse import ArgumentParser
from progressbar import ProgressBar, Bar

from relevence_db import *

class DBLoadBidwordKernel(Thread):

    def __init__(self, seg_file, base_number, serial_number):

        self.seg_file = seg_file
        self.base_number = base_number
        self.serial_number = serial_number
        super(DBLoadBidwordKernel, self).__init__()

    def run(self):

        engine, session = connect_database()
    
        print "computing mean_vec ..."
        mean_vec = None
        word_query = session.query(Word)
        word_count = word_query.count()
        current_count = 0
        progress = ProgressBar(maxval = word_count).start()
        for word in word_query:
            if mean_vec is None:
                mean_vec = zeros(len(loads(word.vector)), dtype = "float32")
            mean_vec += loads(word.vector)
            current_count += 1
            progress.update(current_count)
        mean_vec /= word_count
        progress.finish()
        print "word count", word_query.count()
    
        with open(self.seg_file, "r", encoding = "utf-8") as fp:
            counter = 0
            iterator = 0
            for line in fp:
                if iterator % self.base_number == self.serial_number:
                    iterator += 1
                else:
                    iterator += 1
                    continue
                bidword_str = line.strip()
                word_list = bidword_str.split()
                if word_list is None or len(word_list) == 0:
                    continue
                word_count = 0
                vector = zeros(mean_vec.shape, dtype = "float32")
                for word in word_list:
                    word_record = session.query(Word).filter(Word.context == word.encode("utf-8")).first()
                    if word_record is not None:
                        vector += loads(word_record.vector)
                        word_count += 1
                    if word_count > 0:
                        vector /= word_count
                    else:
                        vector = mean_vec
                bidword = Bidword(context = bidword_str.encode("utf-8"), vector = str(vector))
                session.add(bidword)
                counter += 1
                print self.serial_number, iterator, counter
                if (counter % 1000 == 0):
                    session.commit()
            session.commit()

class DBLoadQueryKernel(Thread):

    def __init__(self, seg_file, base_number, serial_number):

        self.seg_file = seg_file
        self.base_number = base_number
        self.serial_number = serial_number
        super(DBLoadQueryKernel, self).__init__()

    def run(self):

        engine, session = connect_database()
    
        print "computing mean_vec ..."
        mean_vec = None
        word_query = session.query(Word)
        word_count = word_query.count()
        current_count = 0
        progress = ProgressBar(maxval = word_count).start()
        for word in word_query:
            if mean_vec is None:
                mean_vec = zeros(len(loads(word.vector)), dtype = "float32")
            mean_vec += loads(word.vector)
            current_count += 1
            progress.update(current_count)
        mean_vec /= word_count
        progress.finish()
        print "word count", word_query.count()
    
        with open(self.seg_file, "r", encoding = "utf-8") as fp:
            counter = 0
            iterator = 0
            for line in fp:
                if iterator % self.base_number == self.serial_number:
                    iterator += 1
                else:
                    iterator += 1
                    continue
                query_str = line.strip()
                word_list = query_str.split()
                if word_list is None or len(word_list) == 0:
                    continue
                word_count = 0
                vector = zeros(mean_vec.shape, dtype = "float32")
                for word in word_list:
                    word_record = session.query(Word).filter(Word.context == word.encode("utf-8")).first()
                    if word_record is not None:
                        vector += loads(word_record.vector)
                        word_count += 1
                    if word_count > 0:
                        vector /= word_count
                    else:
                        vector = mean_vec
                query = Query(context = query_str.encode("utf-8"), vector = str(vector))
                session.add(query)
                counter += 1
                print self.serial_number, iterator, counter
                if (counter % 1000 == 0):
                    session.commit()
            session.commit()

def load_dict(input_file):

    print "loading json %s ..." % input_file
    with open(input_file, "r", encoding = "utf-8") as fp:
        json_dict = loads(fp.read(), encoding = "utf-8")
    return json_dict

def db_load_word(json_file):

    word_dict = load_dict(json_file)
    engine, session = connect_database()
    
    print "db loading word ..."
    progress = ProgressBar(maxval = len(word_dict)).start()
    counter = 0
    for key in word_dict:
        word = Word(context = key, vector = str(word_dict[key]))
        session.add(word)
        counter += 1
        progress.update(counter)
    session.commit()
    progress.finish()

def db_load_bidword(seg_file, thread_number = 5):

    thread_list = []
    for i in range(thread_number):
        thread_list.append(DBLoadBidwordKernel(seg_file, thread_number, i))

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()
        

def db_load_query(seg_file, thread_number = 2):

    thread_list = []
    for i in range(thread_number):
        thread_list.append(DBLoadQueryKernel(seg_file, thread_number, i))

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()
        
def main():

    parser = ArgumentParser()
    parser.add_argument("input_file", help = "word2vec file in json format")
    parser.add_argument("table_name", help = "table name")
    args = parser.parse_args()
    
    input_file = args.input_file
    table_name = args.table_name

    func_dict = {
        "word": db_load_word,
        "bidword": db_load_bidword,
        "query": db_load_query
    }
        
    func_dict[table_name](input_file)

if __name__ == "__main__":

    main()

