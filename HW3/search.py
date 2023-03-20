#!/usr/bin/python3
import sys
import getopt
from nltk import word_tokenize
from nltk.stem.porter import PorterStemmer
from collections import defaultdict
from math import log, sqrt
import heapq
import time
import util


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
    start_time = time.perf_counter()
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
    print("Queried all in ({:.2f}s)".format(time.perf_counter() - start_time))
    print('result generated.')

# Adapted from Lecture 7 slide 36
def evaluate_query(query, dictionary, postings_file, doc_lengths):
    '''
    Evaluates the query to return the top 10 values
    :param query: the query to be evaluated
    :param dictionary: the dictionary containing term -> offset for posting list
    :param postings_file: the posting list file written to disk
    :param doc_lengths: dictionary containing length of all documents in the corpus
    '''
    # tokeinze, stem, case folding
    stemmer = PorterStemmer()
    tokens = word_tokenize(query)
    tokens = [stemmer.stem(token.lower()) for token in tokens]

    query_weight = defaultdict(float)
    score = defaultdict(float)
    N = len(doc_lengths)

    for token in tokens:
        query_weight[token] += 1
    
    for token in set(tokens):
        # https://stackoverflow.com/questions/9047364/how-to-check-for-a-key-in-a-defaultdict-without-updating-the-dictionary-python
        if token not in dictionary:
            # token does not exist in the corpora
            posting_list = []
        else:
            # calculate the offset in the posting list
            offset = dictionary[token]
            # retrieve the posting list
            posting_list = util.get_posting_list(postings_file, offset)
        
        # number of docs that contain the token
        df = len(posting_list)

        # base case, in case no documents contain the token
        if df <= 0:
            idf = 0
        else:
            # calculate the idf
            idf = log(N / df, 10)

        # calculate the weight of the query
        query_weight[token] = idf * util.log_tf(query_weight[token])

        # calculate the score of the document
        for doc_id_tf_pair in posting_list:
            doc_id, tf = doc_id_tf_pair
            score[doc_id] += query_weight[token] * tf

    # calculate query length
    query_length = 0
    for freq in query_weight.values():
        query_length += freq * freq 

    query_length = sqrt(query_length)

    # normalization
    for doc_id, doc_score in score.items():
        score[doc_id] = doc_score / (doc_lengths[doc_id] * query_length)

    # return the top 10 documents
    # adapted from: https://stackoverflow.com/questions/7197315/5-maximum-values-in-a-python-dictionary
    return heapq.nlargest(TOP_K, score, key=score.__getitem__)
    
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
