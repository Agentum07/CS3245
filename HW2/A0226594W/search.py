#!/usr/bin/python3
import re
import nltk
import sys
import getopt
from math import ceil, sqrt
from nltk import word_tokenize
from nltk.stem.porter import PorterStemmer

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('retrieving the dictionary...')
    dictionary = load_dict(dict_file)
    doc_ids = load_doc_ids('doc_ids.txt')
    print('running search on the queries...')

    queries = open(queries_file, 'r')
    results = open(results_file, 'w')
    query_results = []
    for query in queries:
        result = evaluate_query(query, doc_ids, dictionary, postings_file)
        # print("-=--=-=-=--=----=-=----=-=-=--=-=-=--=-=")
        # print(result)
        query_results.append(result)
    
    text = ""
    for query_result in query_results:
        for val in query_result:
            text += str(val) + " "
        text += "\n"
    results.write(text)
    print('result generated.')


# loads the list of doc_ids from the memory.
def load_doc_ids(doc_id_file):
    doc_ids = []
    memory_doc_id = open(doc_id_file, 'r')
    file_content = memory_doc_id.read()
    
    for doc_id in file_content.split(";"):
        doc_ids.append(int(doc_id))
    
    return doc_ids


# loads the dictionary from the memory.
def load_dict(dict_file):
    dictionary = {}
    memory_dict = open(dict_file, 'r')
    file_content = memory_dict.read()
    
    # breaks the content into [content, "\n"]
    dict_text_list = file_content.split("\n")[:-1]
    for item in dict_text_list:
        token, posting_offset = item.split(" ")
        dictionary[token] = int(posting_offset)

    return dictionary


# loads the posting list from the given offset (offset marks the start of the line in the posting.txt)
def load_posting_list(postings_file, offset):
    postings = open(postings_file, 'r')
    postings.seek(0)
    posting_list = []
    try:
        postings.seek(offset)
        posting_string_list =  postings.readline().rstrip("\n").split(" ")[1:] # get posting list for term
        for values in posting_string_list:
            split_val = values.split("|")
            curr = split_val[0]
            next = -1
            if len(split_val) == 2:
                next = split_val[1]
            posting_list.append((int(curr), int(next)))

    except:
        posting_list = ()
    return posting_list


# takes intersection of multiple tuples, returns final tuple
def intersection(lists_to_intersect):
    # list is empty
    if not lists_to_intersect:
        return ()
    
    sorted_list = sorted(lists_to_intersect, key=len)
    result = sorted_list[0]
    for i in range(1, len(sorted_list)):
        result = eval_and(result, sorted_list[i])

    return result


# takes union of multiple tuples, returns final tuple
def union(lists_to_union):
    # list is empty
    if not lists_to_union:
        return ()

    lists_to_union = list(lists_to_union)
    result = lists_to_union[0]

    for i in range(1, len(lists_to_union)):
        result = eval_or(result, lists_to_union[i])

    return result


# retrieves the posting list for the token.
def retrieve_posting_list_for_token(token, dictionary, postings_file, doc_ids, is_not):
    posting_list = ()
    if token in dictionary:
        posting_list = load_posting_list(postings_file, dictionary[token])
    if is_not:
        posting_list = eval_not(posting_list, doc_ids)
    return tuple(posting_list)


# enum for readability
class Token:
    AND = "and"
    OR = "or"
    NOT = "not"
    LB = "("
    RB = ")"


# evaluates the query
def evaluate_query(query, doc_ids, dictionary, postings_file):
    stemmer = PorterStemmer()
    tokens = word_tokenize(query)
    tokens = [stemmer.stem(token.lower()) for token in tokens]

    final_result = []

    # Base cases
    # A
    if (len(tokens) == 1):
        if tokens[0] in dictionary:
            final_result = load_posting_list(postings_file, dictionary[tokens[0]])
    # NOT A
    elif len(tokens) == 2:
        if tokens[1] in dictionary:
            final_result = eval_not(load_posting_list(postings_file, dictionary[tokens[1]]), doc_ids)
    # Multi term multi operation query
    else:
        ands, ors = set(), set()
        is_and, is_or, is_not = False, False, False
        starting_operation = ""
        first_token_result = ""
        i = 0
        while i < len(tokens):
            token = tokens[i]
            # print(token, "| AND:", is_and, "OR:", is_or, "NOT:", is_not)
            # create a query token class
            if token not in [Token.AND, Token.OR, Token.NOT, Token.LB, Token.RB]:
                if is_not:
                    posting_list = retrieve_posting_list_for_token(token, dictionary, postings_file, doc_ids, True)
                    if is_and:
                        ands.add(posting_list)
                        is_and = False
                    if is_or:
                        ors.add(posting_list)
                        is_or = False
                    
                    is_not = False

                elif is_and:
                    posting_list = retrieve_posting_list_for_token(token, dictionary, postings_file, doc_ids, False)
                    ands.add(posting_list)
                    is_and = False
                
                elif is_or:
                    posting_list = retrieve_posting_list_for_token(token, dictionary, postings_file, doc_ids, False)
                    ors.add(posting_list)
                    is_or = False

            elif token == Token.AND:
                if starting_operation == "":
                    starting_operation = Token.AND
                is_and = True

            elif token == Token.OR:
                if starting_operation == "":
                    starting_operation = Token.OR
                is_or = True

            elif token == Token.NOT:
                # query is => NOT NOT A which is equivalent to A
                if is_not:
                    is_not = False
                    sub_query = tokens[i + 1]
                    sub_query_result = build_skip_list(evaluate_query(sub_query, doc_ids, dictionary, postings_file))
                else:
                    is_not = True
            
            # reached a subquery
            elif token == Token.LB:
                # A AND (B OR C) AND D
                # treat (B OR C) as a new query, recurse
                end_index = i + 1
                while tokens[end_index] != ")":
                    end_index += 1 

                sub_query = ' '.join(tokens[i + 1 : end_index])
                sub_query_result = build_skip_list(evaluate_query(sub_query, doc_ids, dictionary, postings_file))
                # print("Evaluated subquery", sub_query, "length: ", len(sub_query_result))
                if starting_operation == "":
                    first_token_result = sub_query_result

                if is_not:
                    if is_and:
                        ands.add(eval_not(sub_query_result, doc_ids))
                        is_and = False
                    if is_or:
                        ors.add(eval_not(sub_query_result, doc_ids))
                        is_or = False
                    is_not = False
                elif is_and:
                    ands.add(sub_query_result)
                    is_and = False
                elif is_or:
                    ors.add(sub_query_result)
                    is_or = False

                i = end_index
                # print("At the end of subquery evaluation")
                continue

            elif token == Token.RB:
                i += 1
                continue

            if starting_operation == "":
                first_token_result = retrieve_posting_list_for_token(token, dictionary, postings_file, doc_ids, False)
            else:
                if starting_operation == Token.OR:
                    ors.add(first_token_result)
                else:
                    ands.add(first_token_result)
            
            # print("After token", token, "ands:", len(ands), "ors", len(ors))
            i += 1
        

        # evaluate all ands
        final_ands = intersection(ands)
        # evaluate all ors
        final_ors = union(ors)
        # print("final_ands:", len(final_ands), "final_ors:", len(final_ors))
        
        if starting_operation == Token.AND:
            # Query is of the form: A AND B OR C which reduces to => D OR C
            if final_ors:
                # do ands or ors
                final_result = eval_or(final_ands, final_ors)
            else:
                final_result = final_ands
        elif starting_operation == Token.OR:
            if final_ands:
                # do ands AND ors
                # query is of the form: A OR B AND C which reduces to => A OR D
                final_result = eval_and(final_ands, final_ors)
            else:
                final_result = final_ors
        else:
            # The query is of the form: (query) | just 1 bracket
            final_result = sub_query_result

    final_result = convert_tuple_to_list(final_result)
    # print("final_result:", final_result)
    return tuple(final_result)


# performs a "boolean and" on 2 lists
# adapted from lecture 3 slide 8
def eval_and(list1, list2):
    # initialize skip pointers
    skip1 = ceil(sqrt(len(list1)))
    skip2 = ceil(sqrt(len(list2)))
    index1 = 0
    index2 = 0
    result = []
    # ((element, skip)) -> ((9, 5), (0, -1))
    while index1 < len(list1) and index2 < len(list2) :
        doc_id_skip_pair_1 = list1[index1]
        doc_id_skip_pair_2 = list2[index2]
        if (doc_id_skip_pair_1[0] == doc_id_skip_pair_2[0]):
            result.append(doc_id_skip_pair_1)
            index1 += 1
            index2 += 1
        
        elif doc_id_skip_pair_1[0] < doc_id_skip_pair_2[0]:
            if (doc_id_skip_pair_1[1] != -1) and (doc_id_skip_pair_1[1] < doc_id_skip_pair_2[0]) :
                index1 += skip1
            else:
                index1 += 1
        elif doc_id_skip_pair_2[0] < doc_id_skip_pair_1[0]:
            if (doc_id_skip_pair_2[1] != -1) and (doc_id_skip_pair_2[1] < doc_id_skip_pair_1[0]) :
                index2 += skip2
            else:
                index2 += 1
    
    return build_skip_list(convert_tuple_to_list(result))


# joins 2 lists
def eval_or(list1, list2):
    result = []
    index1 = 0
    index2 = 0

    while index1 < len(list1) and index2 < len(list2) :
        doc_id_skip_pair_1 = list1[index1]
        doc_id_skip_pair_2 = list2[index2]
        if (doc_id_skip_pair_1[0] == doc_id_skip_pair_2[0]):
            result.append(doc_id_skip_pair_1)
            index1 += 1
            index2 += 1
        if index1 < len(list1) and index2 < len(list2) and doc_id_skip_pair_1[0] < doc_id_skip_pair_2[0]:
            result.append(doc_id_skip_pair_1)
            index1 += 1

        if index1 < len(list1) and index2 < len(list2) and doc_id_skip_pair_2[0] < doc_id_skip_pair_1[0]:
            result.append(doc_id_skip_pair_2)
            index2 += 1

    while index1 < len(list1):
        doc_id_skip_pair_1 = list1[index1]
        result.append(doc_id_skip_pair_1)
        index1 += 1

    while index2 < len(list2):
        doc_id_skip_pair_2 = list2[index2]
        result.append(doc_id_skip_pair_2)
        index2 += 1

    return build_skip_list(convert_tuple_to_list(result))


# set difference operation, done with tuples
def eval_not(list1, doc_ids):
    if (not list1):
        return doc_ids
    
    result = []
    list1 = convert_tuple_to_list(list1)
    for doc_id in doc_ids:
        if doc_id not in list1:
            result.append(doc_id)

    return build_skip_list(result)


# builds the skip list for the posting_list, returns a tuple of tuples. ((doc_id, skip_val), (doc_id, -1), (),...)
# -1 indicates skip does not exist.
def build_skip_list(posting_list):
    skip_list = []
    jump = ceil(sqrt(len(posting_list)))
    for idx, posting in enumerate(posting_list):
        if idx % jump == 0 and (idx + jump) < len(posting_list):
            next_val = posting_list[idx + jump]
            skip_list.append((posting, next_val))
        else:
            skip_list.append((posting, -1))
    
    return tuple(skip_list)


# converts the tuple of tuples back to a list.
def convert_tuple_to_list(tuple_of_tuples):
    final_list = set()
    for tuple in tuple_of_tuples:
        final_list.add(tuple[0])
    return sorted(list(final_list))

dictionary_file = postings_file = file_of_queries = output_file_of_results = None


# dictionary = load_dict('dictionary.txt')
# doc_ids = load_doc_ids('doc_ids.txt')
# print(evaluate_query("(copper AND nickel) OR (gold AND platinum)", doc_ids, dictionary, 'postings.txt'))

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
