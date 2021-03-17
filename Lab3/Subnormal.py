import argparse
import TFIDFViewer as tf
from itertools import islice

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q


#python3 Rocchio.py --index --query --nrounds --k --R --a --b

# More precisely, we want our script to do the following:
# 1. Ask for a set of words to use as query
# 2. For a number of times (nrounds):
# (a) Obtain the k more relevant documents
# (b) Compute a new query applying Rocchio’s rule to the current query and the Tf-Idf representation of the k documents
# 3. Return the k most relevant documents after the n iterations

def calculate_tfidf(query, docs, client, index):
    tfidf = {}

    for w,_ in query.items():
        tfidf[w] = 0

    for d in docs:
        doc_id = tf.search_file_by_path(client,index, d.path)
        doc_tw = tf.toTFIDF(client, index, doc_id)
        dic_tw = dict(doc_tw)

        for w,_ in query.items():
            tfidf[w] += dic_tw[w] 

        return tfidf

def query_to_dic(q):
    dicc = {}
    for word in query:
        if "^" not in word:
            dicc[word] = 1
        else:
            x = word.split("^")
            dicc[x[0]] = x[1]
    return dicc

def dic_to_query(dic):
    res = ""
    for q,w in dic.items():
        weigth = str(int(w))
        res += q + "^" + weigth + " "
    return res

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--nrounds', default=None, type=int, help='the number of applications of Rocchio’s rule')
    parser.add_argument('--k', default=None, type=int, help='the number of top documents considered relevant')
    parser.add_argument('--R', default=None, type=int, help='the maximum number of new terms')
    parser.add_argument('--a', default=None, type=float, help='the weights in the Rocchio rule.')
    parser.add_argument('--b', default=10, type=float, help='the weights in the Rocchio rule.')
    parser.add_argument('--index', default=None, help='Index to search')
    parser.add_argument('--query', default=None, nargs=argparse.REMAINDER, help='List of words to search')

    args = parser.parse_args()
    index = args.index
    query = args.query
    nrounds = args.nrounds
    k = args.k
    R = args.R
    a = args.a
    b = args.b
    print(query)

    try:
        client = Elasticsearch()
        s = Search(using=client, index=index)

        if query is not None:
            q = Q('query_string',query=query[0])
            for i in range(1, len(query)):
                q &= Q('query_string',query=query[i])

            s = s.query(q)
            response = s[0:k].execute()

            dicc = query_to_dic(query)
            print("Iteration: %s ::: query = %s" % ('1', query))

            ##ROCCHIO
            tfidf = calculate_tfidf(dicc, response, client, index)
            
            for i in range(3, nrounds):
                for w, wei in dicc.items():
                    # query = alpha * query + beta * (d1+d2.../k)
                    dicc[w] = int(a) * int(wei) + int(b) + int((tfidf[w] / k))

                new_q = dic_to_query(dicc)
                print("Iteration: %s ::: query = %s" % (str(i-1), new_q))

                q = Q('query_string',query=query[0])
                for i in range(1, len(query)):
                    q &= Q('query_string',query=query[i])

                s = s.query(q)
                response = s[0:k].execute() ###k relevant docs
                tfidf = calculate_tfidf(dicc, response, client, index)

            #last
            for w, wei in dicc.items():
                    dicc[w] = int(a) * int(wei) + int(b) * int((tfidf[w]/k))
            new_q = dic_to_query(dicc)
            print("Iteration: %s ::: query = %s" % (str(nrounds), new_q))

            q = Q('query_string',query=new_q[0])

            x=0
            if (R > len(new_q)):
                x = len(new_q)
            else: x = R

            for i in range(1, x):
                q &= Q('query_string',query=new_q[i])
            s = s.query(q)
            response = s[0:k].execute()

            for r in response:  # only returns a specific number of results
                print(f'ID= {r.meta.id} SCORE={r.meta.score}')
                print(f'PATH= {r.path}')
                print(f'TEXT: {r.text[:50]}')
                print('-----------------------------------------------------------------')

        else:
            print('No query parameters passed')

        print (f"{response.hits.total['value']} Documents")

    except NotFoundError:
        print(f'Index {index} does not exists')

