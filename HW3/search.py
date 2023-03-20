#!/usr/bin/python3
import sys
import getopt
from nltk import word_tokenize
from nltk.stem.porter import PorterStemmer
from collections import defaultdict
from math import log, sqrt
import heapq
import util

# the number of 
TOP_K = 10

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print("loading dictionary")
    dictionary = util.load_dict(dict_file)
    doc_lengths = util.load_doc_lengths('doc_lengths.txt')

    print('running search on the queries...')
    # This is an empty method
    # Pls implement your code in below
    queries = open(queries_file, 'r')
    results = open(results_file, 'w')

    query_results = []
    for query in queries:
        result = evaluate_query(query, dictionary, postings_file, doc_lengths)
        result = util.format_result(result)
        query_results.append(result)

    final_text = "\n".join(query_results)
    results.write(final_text)
    print('result generated.')


def evaluate_query(query, dictionary, postings_file, doc_lengths):
    '''
    Evaluates the query to return the top 10 values
    :param query: the query to be evaluated
    :param query: the query to be evaluated
    :param query: the query to be evaluated
    :param query: the dictionary containing
    '''
    stemmer = PorterStemmer()
    tokens = word_tokenize(query)
    tokens = [stemmer.stem(token.lower()) for token in tokens]

    tf_query = defaultdict(float)
    document_score = defaultdict(float)
    N = len(doc_lengths)

    for token in tokens:
        tf_query[token] += 1
    
    for token in set(tokens):
        # https://stackoverflow.com/questions/9047364/how-to-check-for-a-key-in-a-defaultdict-without-updating-the-dictionary-python
        if token not in dictionary:
            posting_list = []
        else:
            offset = dictionary[token]
            posting_list = util.get_posting_list(postings_file, offset)
        
        df = len(posting_list) # number of docs that contain the token

        if df <= 0:
            idf = 0
        else:
            idf = log(N / df, 10)

        tf_query[token] = idf * util.log_tf(tf_query[token])

        for doc_id_tf_pair in posting_list:
            doc_id, tf = doc_id_tf_pair
            document_score[doc_id] += tf_query[token] * tf

        # if you make it counter document_score 

        # then normalise document_score 
        # document_score.most_common(10)

    query_length = 0
    for freq in tf_query.values():
        query_length += freq * freq 

    query_length = sqrt(query_length)

    for doc_id, doc_score in document_score.items():
        document_score[doc_id] = doc_score / (doc_lengths[doc_id] * query_length)

    return heapq.nlargest(TOP_K, document_score, key=document_score.__getitem__)
    
dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
