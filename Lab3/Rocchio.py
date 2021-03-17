"""
.. module:: SearchIndexWeight

SearchIndex
*************

:Description: SearchIndexWeight

    Performs a AND query for a list of words (--query) in the documents of an index (--index)
    You can use word^number to change the importance of a word in the match

    --nhits changes the number of documents to retrieve

:Authors: bejar
    

:Version: 

:Created on: 04/07/2017 10:56 

"""

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError

import argparse

from elasticsearch_dsl import Search
from elasticsearch_dsl.query import Q


from elasticsearch.client import CatClient
import numpy as np

def queryToDic(query):
    dic={}
    for elem in query:
        if '^' in elem:
            name, value = elem.split('^')
            value = float(value)
        else:
            name = elem
            value = 1
        dic[name] = value
    return dic

def dicToQuery(dic):
    newQuery=[]
    for elem in dic:
        newQuery.append(elem + '^' + str(dic[elem]))
    return newQuery

######################## FUNCIONES DE TFIDF #############################

def document_term_vector(client, index, id):
    """
    Returns the term vector of a document and its statistics a two sorted list of pairs (word, count)
    The first one is the frequency of the term in the document, the second one is the number of documents
    that contain the term

    :param client:
    :param index:
    :param id:
    :return:
    """
    termvector = client.termvectors(index=index, id=id, fields=['text'],
                                    positions=False, term_statistics=True)

    file_td = {}
    file_df = {}

    if 'text' in termvector['term_vectors']:
        for t in termvector['term_vectors']['text']['terms']:
            file_td[t] = termvector['term_vectors']['text']['terms'][t]['term_freq']
            file_df[t] = termvector['term_vectors']['text']['terms'][t]['doc_freq']
    return sorted(file_td.items()), sorted(file_df.items())

def doc_count(client, index):
    """
    Returns the number of documents in an index

    :param client:
    :param index:
    :return:
    """
    return int(CatClient(client).count(index=[index], format='json')[0]['count'])

################### MODIFICAR FUNCIONES DE TFIDF PARA QUE FUNCIONEN CON DICCIONARIOS (ORIGINALMENTE LISTAS)###########

def toTFIDF(client, index, file_id):
    """
    Returns the term weights of a document

    :param file:
    :return:
    """

    # Get the frequency of the term in the document, and the number of documents
    # that contain the term
    file_tv, file_df = document_term_vector(client, index, file_id)
    max_freq = max([f for _, f in file_tv])

    dcount = doc_count(client, index)

    tfidfw = {}
    for (t, w),(_, df) in zip(file_tv, file_df):
        # TFIDF = freq(element) / max(freq(actDoc)) * log2(#DOCUMENTS/#DOCUMENTS(element))
        actTf = (w/max_freq) * np.log2(dcount/df)
        tfidfw[t]= actTf
    return normalize(tfidfw)

def normalize(tw):
    """
    Normalizes the weights in t so that they form a unit-length vector
    It is assumed that not all weights are 0
    :param tw:
    :return:
    """

    norm = np.sqrt(sum(tw[elem]**2 for elem in tw))
    normalizedVec={}
    for elem in tw:
        normalizedVec[elem] = tw[elem]/norm

    return normalizedVec

################################################################################
__author__ = 'bejar'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index'   ,default=None, help='Index to search')
    parser.add_argument('--query'   , default=None, nargs=argparse.REMAINDER, help='List of words to search')

    args = parser.parse_args()

    index   = args.index
    # QUERY ARRAY CON CADA ELEMENTO DE --query
    query   = args.query

    alpha   = 2
    beta    = 1
    R       = 4
    k       = 10
    nrounds = 15

    try:
        # CREAR CLIENT ELASTISCSEARCH
        client = Elasticsearch()
        # CREAR GESTOR PETICIONS
        s = Search(using=client, index=index)
        if query is not None:
            for iteration in range(nrounds):
                if query is not None:
                
                    # Q GENERA UNA QUERY I AGAFAM EL PRIMER ELEMENT
                    q = Q('query_string',query=query[0])
                    for i in range(1, len(query)):
                        # PER CADA VALOR EXTRA DINS QUERY REALITZA UNA AND
                        q &= Q('query_string',query=query[i])

                    # GENERA LA QUERY A LA BASE DE DADES
                    s = s.query(q)
                    # REALITZA LA QUERY A LA BASE DE DADES SI k > len(s) IGNORA I PARA AL LLEGAR A len(s)
                    response = s[0:k].execute()

                    dicOriginalQuery = normalize(queryToDic(query))
                    documentSum={}

                    # PARA COMO MUCHO LOS k IMPRIME CADA DOC
                    for r in response:  # only returns a specific number of results
                        docTFIDF = toTFIDF(client,index, r.meta.id) # CALCULAR TFIDF VECTOR
                        documentSum = {elem:  documentSum.get(elem,0) + docTFIDF.get(elem,0) for elem in set(documentSum) | set(docTFIDF) } # PER CADA TERME SUMAR EL VALOR ACTUAL MES EL NOU
                        # print(f'ID= {r.meta.id} SCORE={r.meta.score}')
                        # print(f'PATH= {r.path}')
                        # print(f'TEXT: {r.text[:50]}')
                        # print('----------------------------------------------------')
                    # APLICAR LA FORMULA DE ROCCHIO q' = alpha * q + beta * (d1 + d2 + .. + dk)/k
                    vectorResult  = {elem: documentSum.get(elem,0)*beta/k for elem in documentSum}
                    originalQuery = {elem: dicOriginalQuery.get(elem,0)*alpha for elem in dicOriginalQuery}
                    newQuery      = {elem: originalQuery.get(elem,0) + vectorResult.get(elem,0) for elem in set(originalQuery) | set(vectorResult)}
                    # ORDENAR QUERY PER ORDRE DE PES -> sorted RETORNA UNA LLISTA DE TUPLES
                    newQuery      = sorted(newQuery.items(), key=lambda x:x[1], reverse=True)
                    # SELECCIONAR ELS PRIMERS R VALORS
                    newQuery      = newQuery[:R]
                    #PASSAR LLISTA DE QUERY A DICCIONARI I POSTERIORMENT GENERAR LA QUERY PER NOVA ITERACIO
                    query = dicToQuery(normalize(dict(newQuery)))

        else:
            print('No query parameters passed')

        for r in response:  # only returns a specific number of results
            print(f'ID= {r.meta.id} SCORE={r.meta.score}')
            print(f'PATH= {r.path}')
            print(f'TEXT: {r.text[:50]}')
            print('----------------------------------------------------')
        print (f"{response.hits.total['value']} Documents")
        print(query)
    except NotFoundError:
        print(f'Index {index} does not exists')

