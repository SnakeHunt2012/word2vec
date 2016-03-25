#!/usr/bin/env python
# -*- coding: utf-8

from time import ctime
from numpy import array, dot, sqrt
from prettytable import PrettyTable

from relevence_db import *

def vector_to_array(vector):

    return array(vector.strip().lstrip("[").rstrip("]").split(), dtype = "float32")

def main():

    engine, session = connect_database()
    query_query = session.query(Query)
    for query in query_query:
        print "==================================================================="
        print
        query_vector = vector_to_array(query.vector)
        query_norm = sqrt(dot(query_vector, query_vector))
        print "Query:", query.context.encode("utf-8")
        print "Norm:", query_norm
        id_score_list = []
        bidword_query = session.query(Bidword)
        for bidword in bidword_query:
            bidword_vector = vector_to_array(bidword.vector)
            bidword_norm = sqrt(dot(bidword_vector, bidword_vector))
            score = dot(query_vector, bidword_vector) / query_norm / bidword_norm
            context = bidword.context
            id_score_list.append((score, context, bidword_norm))
        id_score_list.sort(lambda x, y: cmp(x[0], y[0]),
                            reverse = True)
        table = PrettyTable()
        table.field_names = ["sim", "norm", "Query/Bidwords"]
        for i in range(10000):
            query_token_set = set(query.context.split())
            bidword_token_set = set(id_score_list[i][1].split())
            if len(query_token_set & bidword_token_set) > 0:
                continue
            table.add_row([id_score_list[i][0],
                           id_score_list[i][2],
                           id_score_list[i][1]])
        print
        print table
        print
            

if __name__ == "__main__":

    main()
