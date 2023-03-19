#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import getopt
import math


# Adds all elements of dict1 that don't exist in dict2 to dict2
def combine_dicts(dict1, dict2):
    for key in dict1.keys():
        if key not in dict2:
            dict2[key] = 0


def add_one_smoothing(dict1):
    for key in dict1.keys():
        dict1[key] += 1


# Converts all counts to probability values, then takes log to avoid issues if value gets too small.
def calculate_lang_prob(dict1):
    lang_count = sum(dict1.values())
    lang_dict = {}
    for key in dict1.keys():
        lang_dict[key] = math.log(dict1[key] / lang_count)
    return lang_dict


####################################################################
# Build Language Model -> Add everything to corresponding dictionary
# Add one smoothing: 
# -> calculate C = indonesian + (malaysian - indonesian)
# Add C to indonesian with count 0
# Increment all counts in indonesian by 1.
# Do this 3 times
# calculate probability
####################################################################
def build_LM(in_file):
    """
    build language models for each label
    each line in in_file contains a label and a string separated by a space
    """
    print("building language models...")
    # This is an empty method
    # Pls implement your code below

    # dictionaries containing value counts for all 4grams
    indonesian = {}
    malaysian = {}
    tamil = {}

    # Returns the corresponding dictionary for the language
    def get_dict(lang_char):
        if lang_char == 'i':
            return indonesian
        elif lang_char == 'm':
            return malaysian
        else:
            return tamil

    with open(in_file) as f:
        lines = f.readlines()
    lines = [x.rstrip("\n") for x in lines]
    lang_dict = {}

    # build our data structure. this adds the counts of all 4grams for a specific language.
    for line in lines:
        lang_dict = get_dict(line[0].lower())
        
        # '{' is the START token and '}' is the END token
        line = "{{{" + ' '.join(line.split(' ')[1:]) + "}}}"
        four_grams = [line[i: i + 4] for i in range(len(line) - 4 + 1)]
        for four_gram in four_grams:
            try:
                lang_dict[tuple(four_gram)] += 1
            except:
                lang_dict[tuple(four_gram)] = 1

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
    indo_probs_dict = calculate_lang_prob(indonesian)
    malay_probs_dict = calculate_lang_prob(malaysian)
    tamil_probs_dict = calculate_lang_prob(tamil)

    # now we have dictionaries containing the probabilities of all vocabulary.
    # we're done building the language model!
    return indo_probs_dict, malay_probs_dict, tamil_probs_dict


def test_LM(in_file, out_file, LM):
    """
    test the language models on new strings
    each line of in_file contains a string
    you should print the most probable label for each string into out_file
    """
    print("testing language models...")
    # This is an empty method
    # Pls implement your code below
    with open(in_file) as input_file:
        lines = input_file.readlines()
    output_file = open(out_file, 'w')
    
    lines = [x.rstrip("\n") for x in lines]
    indo_probs_dict, malay_probs_dict, tamil_probs_dict = LM 

    for line in lines:
        # code taken from: https://stackoverflow.com/a/69793069
        four_grams = [line[i: i + 4] for i in range(len(line) - 4 + 1)]
        lang_dict = {}
        for four_gram in four_grams:
            try:
                lang_dict[tuple(four_gram)] += 1
            except:
                lang_dict[tuple(four_gram)] = 1
        
        indo_prob, malay_prob, tamil_prob = 0.0, 0.0, 0.0

        for key in lang_dict.keys():
            try:
                malay_prob += malay_probs_dict[key]
                tamil_prob += tamil_probs_dict[key]
                indo_prob += indo_probs_dict[key]
            except:
                # tuple doesn't exist.
                pass
        
        predicted_language = ""
        # the try catch block failed for the entire input. language is unknown.
        if (indo_prob == malay_prob and malay_prob == tamil_prob and indo_prob == 0.0):
            predicted_language = "other "
        else:
            predicted_language = ("indonesian " if (indo_prob > malay_prob and indo_prob > tamil_prob) else 
                              ("malaysian " if (malay_prob > indo_prob and malay_prob > tamil_prob) else "tamil "))
        
        output_text = predicted_language + line + "\n"
        output_file.write(output_text)


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
