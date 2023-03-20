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
from collections import defaultdict
import util

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
                        posting_list[word] = {}

                    if doc_id not in posting_list[word]:
                        posting_list[word][doc_id] =  1
                    else:
                        posting_list[word][doc_id] +=  1

        # calculate the length of each doc as explained on piazza
        doc_length[doc_id] = util.calculate_doc_length(posting_list, doc_id)
        
    # convert freqs to tf
    for word in posting_list:
        # print(word, posting_list[word])
        for doc_id, term_freq in posting_list[word].items():
            posting_list[word][doc_id] = util.log_tf(term_freq)

    # format posting list to be more readable
    posting_list = util.format_posting_list(posting_list)

    # save posting list and dictionary
    util.save_posting_list_and_dictionary(posting_list, out_postings, out_dict)
    util.save_doc_lengths(doc_length, 'doc_lengths.txt')

    print("Indexed in ({:.2f}s)".format(time.perf_counter() - start_time))
    print('indexing complete.')

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
