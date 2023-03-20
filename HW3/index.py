#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os
from nltk import sent_tokenize, word_tokenize
from nltk.stem.porter import PorterStemmer
import time
import math
import pickle
from collections import Counter, defaultdict

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")


# resets the directory, deletes the existing dictionary, posting lists written to disk.
def reset_dir(out_dict, out_postings, out_doc_lengths):
    if os.path.exists(out_dict):
        os.remove(out_dict)
    if os.path.exists(out_postings):
        os.remove(out_postings)
    if os.path.exists(out_doc_lengths):
        os.remove(out_doc_lengths)

def log_tf(term_freq):
    weight = 0
    if term_freq > 0:
        weight = 1 + math.log(term_freq, 10)

    return weight

# commands to run
# python HW3/index.py -i "" -d HW3/dictionary.txt -p HW3/postings.txt
def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    in_dir = "/Users/a65888/nltk_data/corpora/reuters/training/"
    reset_dir(out_dict, out_postings, 'doc_lengths.txt')
    start_time = time.perf_counter()

    print('indexing...')
    # save the posting list
    # save the dictionary
    # This is an empty method
    # Pls implement your code in below
    stemmer = PorterStemmer()
    posting_list = defaultdict(lambda: defaultdict(int)) # dict of dict
    doc_length = {} # calculate length of each document to write

    # pre-sort the docids so we can append to posting list directly
    doc_ids = [int(doc_id) for doc_id in os.listdir(in_dir)]
    doc_ids = sorted(doc_ids)

    for doc_id in doc_ids:
        with open(os.path.join(in_dir, str(doc_id)), 'r') as f:
            # read all lines from a doc
            lines = f.read()
            # tokenize them into sentences
            for line in sent_tokenize(lines):
                # tokenize into words
                for word in word_tokenize(line):
                    # case folding and stemming
                    word = stemmer.stem(word.lower())
                    # word has not been seen before
                    if word not in posting_list:
                        # dictionary.add(word)
                        posting_list[word] = {}

                    if doc_id not in posting_list[word]:
                        posting_list[word][doc_id] =  1
                    else:
                        posting_list[word][doc_id] +=  1
        
        # calulate the length of each doc as explained on piazza
        doc_length[doc_id] = calculate_doc_length(posting_list, doc_id)
        
    # convert freqs to tf
    for word in posting_list:
        # print(word, posting_list[word])
        for doc_id, term_freq in posting_list[word].items():
            posting_list[word][doc_id] = log_tf(term_freq)

    # format posting list to be more readable
    posting_list = format_posting_list(posting_list)

    # save posting list and dictionary
    save_posting_list_and_dictionary(posting_list, out_postings, out_dict)
    save_doc_lengths(doc_length, 'doc_lengths.txt')

    print("Indexed in ({:.2f}s)".format(time.perf_counter() - start_time))
    print('indexing complete.')


def save_posting_list_and_dictionary(posting_list, posting_dir, dictionary_dir):
    dictionary = {}
    with open(posting_dir, 'wb') as posting_ptr:
        for word, doc_lst in sorted(posting_list.items()):
            offset = posting_ptr.tell()
            dictionary[word] = offset
            pickle.dump(sorted(doc_lst), posting_ptr)
    posting_ptr.close()

    with open(dictionary_dir, 'wb') as dict_ptr:
        pickle.dump(dictionary, dict_ptr)
    dict_ptr.close()


def save_doc_lengths(doc_length, doc_length_dir):
    with open(doc_length_dir, 'wb') as doc_ptr:
        pickle.dump(doc_length, doc_ptr)
    doc_ptr.close()
    

def calculate_doc_length(posting_list, doc_id):
    doc_N = 0
    term_freq = 0
    for word in posting_list.keys():
        if doc_id in posting_list[word]:
            term_freq += math.pow(log_tf(posting_list[word][doc_id]), 2)
    doc_N = math.sqrt(term_freq)
    return doc_N


def format_posting_list(posting_list):
    """
        Formats from dict to optimised storable and readable data strcture
        {word: {docId: tf}} => [(docId, tf)]
        :param posting_list: of format {word: {docId: tf}}
    """
    final_postings = defaultdict(list)
    for word in posting_list:
        for doc_id, tf in posting_list[word].items():
            final_postings[word].append((doc_id, tf))
    
    return final_postings

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
