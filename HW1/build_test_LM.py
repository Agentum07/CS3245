#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import nltk
import sys
import getopt

indonesian = {}
indonesian_count = 0
malaysian = {}
malaysian_count = 0
tamil = {}
tamil_count = 0


def get_dict(lang_char):
    if lang_char == 'i':
        return (indonesian, indonesian_count)
    elif lang_char == 'm':
        return (malaysian, malaysian_count)
    else:
        return (tamil, tamil_count)
    

def combine_dicts(dict1, dict2):
    for key in dict1.keys():
        if key not in dict2:
            dict2[key] = 0
    
def add_one_smoothing(dict1):
    for key in dict1.keys():
        dict1[key] += 1

def calculate_lang_prob(dict):
    lang_count = sum(dict.values())
    lang_dict = {}
    for key in dict.keys():
        lang_dict[key] = dict[key] / lang_count
    return lang_dict
####################################################################
# Build Language Model -> Add everything to corresponding dictionary
# Add one smoothing 
# -> calculate A + (B - A) = C
# Add C to A with count 0
# Increment all counts in A by 1.
# Do this 3 times. (Create a function for this?)
# calculate probability: maybe use the log method from piazza
####################################################################
def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space
    """
    print("building language models...")
    # This is an empty method
    # Pls implement your code below
    with open(in_file) as f:
        lines = f.readlines()
    
    lines = [x.rstrip("\n") for x in lines]
    lang_dict = {}

    # build our data structure. this has the counts of all tuples for a specific language.
    for line in lines:
        lang_dict, lang_count = get_dict(line[0])
        
        ngrams = [line[i: i + 4] for i in range(len(line) - 4 + 1)]
        for ngram in ngrams:
            lang_count += 1
            try:
                lang_dict[tuple(ngram)] += 1
            except:
                lang_dict[tuple(ngram)] = 1

    # now, add all remaining elements with count = 0 in the other 2 dicts
    combine_dicts(indonesian, malaysian)
    combine_dicts(indonesian, tamil)
    combine_dicts(tamil, malaysian)
    combine_dicts(tamil, indonesian)
    combine_dicts(malaysian, tamil)
    combine_dicts(malaysian, indonesian)

    # now, add one smoothing
    add_one_smoothing(indonesian)
    add_one_smoothing(malaysian)
    add_one_smoothing(tamil)

    # now calculate probabilies
    indo_prob = calculate_lang_prob(indonesian)
    malay_prob = calculate_lang_prob(malaysian)
    tamil_prob = calculate_lang_prob(tamil)
    # now we have dictionary containing the probabilities of all vocabulary.
    # we're done?



def test_LM(in_file, out_file, LM):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    """
    print("testing language models...")
    # This is an empty method
    # Pls implement your code below


def usage():
    print(
        "usage: "
        + sys.argv[0]
        + " -b input-file-for-building-LM -t input-file-for-testing-LM -o output-file"
    )


input_file_b = input_file_t = output_file = None
try:
    opts, args = getopt.getopt(sys.argv[1:], "b:t:o:")
except getopt.GetoptError:
    usage()
    sys.exit(2)
for o, a in opts:
    if o == "-b":
        input_file_b = a
    elif o == "-t":
        input_file_t = a
    elif o == "-o":
        output_file = a
    else:
        assert False, "unhandled option"
if input_file_b == None or input_file_t == None or output_file == None:
    usage()
    sys.exit(2)

LM = build_LM(input_file_b)
test_LM(input_file_t, output_file, LM)
