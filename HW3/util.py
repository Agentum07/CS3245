#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os
from nltk import sent_tokenize, word_tokenize
from nltk.stem.porter import PorterStemmer
import time
from math import log, pow, sqrt
import pickle
from collections import defaultdict

def log_tf(term_freq):
    '''
    Calculates the tf value for the given frequency
    :param term_freq: the freq for which tf value is to be calculated
    '''
    weight = 0
    if term_freq > 0:
        weight = 1 + log(term_freq, 10)

    return weight

######################################################################################
############################## FUNCTIONS FOR INDEX.PY ################################
######################################################################################

def save_posting_list_and_dictionary(posting_list, posting_dir, dictionary_dir):
    '''
    Saves the posting list to memory. Creates a dictionary for the memory as well.
    posting list: {word -> (doc_id, log(term_freq))}
    dictionary: {word -> offset for posting list}

    :param posting_list: posting_list to be written
    :param posting_dir: output file for posting_list to be written
    :param dictionary_dir: output file for dictionary to be written
    '''
    dictionary = defaultdict(int)
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
    '''
    Write the dictionary of doc lengths to memory
    :param doc_length: dictionary to be written
    :param doc_length_dir: directory to be written into
    '''
    with open(doc_length_dir, 'wb') as doc_ptr:
        pickle.dump(doc_length, doc_ptr)
    doc_ptr.close()


def calculate_doc_length(posting_list, doc_id):
    '''
    Calculates the length of each document as mentioned in piazza
    taken from: https://piazza.com/class/la0p9ydharl54v/post/196

    :param posting_list: the created posting list while indexing
    :param doc_id: the document id for which length is being calculated
    '''
    doc_N = 0
    tf = 0
    for word in posting_list.keys():
        if doc_id in posting_list[word]:
            tf += pow(log_tf(posting_list[word][doc_id]), 2)
    doc_N = sqrt(tf)
    return doc_N


def format_posting_list(posting_list):
    '''
    Formats from dict to optimised storable and readable data strcture
    {word: {docId: tf}} => [(docId, tf)]
    :param posting_list: of format {word: {docId: tf}}
    '''
    final_postings = defaultdict(list)
    for word in posting_list:
        for doc_id, tf in posting_list[word].items():
            final_postings[word].append((doc_id, tf))
    
    return final_postings


######################################################################################
############################# FUNCTIONS FOR SEARCH.PY ################################
######################################################################################
def load_dict(dict_file):
    '''
    Loads the dictionary file from the memory
    :param dict_file: location of the text file
    :return: the value stored in the text file
    '''
    with open(dict_file, 'rb') as dict_ptr:
        return pickle.load(dict_ptr)
    

def load_doc_lengths(doc_lengths_file):
    '''
    Loads the doc lengths file from the memory
    :param doc_lengths_file: location of the text file
    :return: the value stored in the text file
    '''
    with open(doc_lengths_file, 'rb') as doc_ptr:
        return pickle.load(doc_ptr)


def get_posting_list(postings_file, offset):
    '''
    Retrieves the posting list from the given offset
    :param postings_file: the text file containing all posting lists
    :param offset: the offset to be read
    '''
    with open(postings_file, 'rb') as posting_ptr:
        posting_ptr.seek(offset)
        return pickle.load(posting_ptr)


def format_result(result):
    """
    Formats result as required for output file
    :param result: In format [10, 1]
    :return: '1 10' formatted string
    """
    formatted_result = list()
    for val in result:
        formatted_result.append(val)

    formatted_result = " ".join(map(str, formatted_result))
    return formatted_result