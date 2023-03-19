#!/usr/bin/python3
import re
from nltk import sent_tokenize, word_tokenize
from nltk.stem.porter import PorterStemmer
import sys
import getopt
import os
import string
import time
import shutil
from math import floor, ceil, sqrt
from queue import PriorityQueue

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

BLOCKS_DIR = "spimi_blocks/"
BLOCK_SIZE = 120_000

# resets the directory, deletes existing spimi blocks, dictionary, posting lists written to disk.
def reset_dir(out_dict, out_postings):
    if os.path.exists(BLOCKS_DIR):
        shutil.rmtree(BLOCKS_DIR)
    os.makedirs(BLOCKS_DIR)

    if os.path.exists(out_dict):
        os.remove(out_dict)
    if os.path.exists(out_postings):
        os.remove(out_postings)


# performs merge on n = total_num_blocks
def n_merge_blocks(total_num_blocks, out_dict, out_postings):
    print("Merge all " + str(total_num_blocks) + " blocks ...")

    num_lines_read = 0
    posting_line_offset = 0
    token_to_write = ''
    doc_id_list_to_write = []
    final_token_docid_list_to_write = []
    final_token_offset_pair_to_write = []
        
    # https://stackoverflow.com/questions/4056768/how-to-declare-array-of-zeros-in-python-or-an-array-of-a-certain-size
    # block_offsets[i] stores the offset value for reading from file of block i
    # file_ptrs[i] stores the pointer to the block file
    # lines_per_block_lst[i] stores the number of lines in each block
    block_offsets = [0] * total_num_blocks
    file_ptrs = [0] * total_num_blocks
    lines_per_block_lst = [0] * total_num_blocks

    for block_num in range(total_num_blocks):
        file_ptrs[block_num] = open(BLOCKS_DIR + str(block_num) + ".txt", 'r')

    posting_file_ptr = open(out_postings, 'a')
    dict_file_ptr = open(out_dict, 'a')

    lines_per_block = floor(BLOCK_SIZE / total_num_blocks)
    if lines_per_block == 0:
        # the block size limit is smaller than the total num of blocks
        lines_per_block = 1

    pq = PriorityQueue()

    for block_num in range(total_num_blocks):
        lines = read_from_file(BLOCKS_DIR + str(block_num), block_offsets[block_num], file_ptrs[block_num], lines_per_block)

        for line in lines:
            block_offsets[block_num] = block_offsets[block_num] + len(line) + 1  # 1 for \n
            pq.put(QueueEntry(line, block_num))
            lines_per_block_lst[block_num] += 1

    # n way merge
    # idea taken from: https://stackoverflow.com/questions/5055909/algorithm-for-n-way-merge
    while not pq.empty():
        # Process head of the queue
        curr_item = pq.get()
        curr_token = curr_item.get_token()
        curr_posting_list = curr_item.get_posting_list()
        curr_block = curr_item.get_block_num()

        # read curr item to memory
        lines_per_block_lst[curr_block] -= 1

        if token_to_write != '' and curr_token != token_to_write:
            skip_ptr_list = build_skip_list(doc_id_list_to_write)
            final_posting_lst_to_write = token_to_write + " " + " ".join(skip_ptr_list) + "\n"
                
            final_token_offset_pair_to_write.append(token_to_write  + " " + str(posting_line_offset) + "\n")
            final_token_docid_list_to_write.append(final_posting_lst_to_write)

            posting_line_offset += len(final_posting_lst_to_write)

            # completed writing posting list of prev term
            num_lines_read += 1
            doc_id_list_to_write = []

        if num_lines_read == BLOCK_SIZE:
            write_file_to_disk(out_dict, "".join(final_token_offset_pair_to_write), dict_file_ptr, True)
            write_file_to_disk(out_postings, "".join(final_token_docid_list_to_write), posting_file_ptr, True)

            # reset
            num_lines_read = 0
            final_token_docid_list_to_write = []
            final_token_offset_pair_to_write = []

        # all lines in current block have been read, read next block
        if lines_per_block_lst[curr_block] == 0:
            lines = read_from_file(BLOCKS_DIR + str(curr_block), block_offsets[curr_block], file_ptrs[curr_block], lines_per_block)
            for line in lines:
                block_offsets[curr_block] = block_offsets[curr_block] + len(line) + 1
                pq.put(QueueEntry(line, curr_block))
                lines_per_block_lst[curr_block] += 1
            
        for doc_id in curr_posting_list:
            doc_id = doc_id.rstrip("\n")
            if doc_id == '':
                continue
            if len(doc_id_list_to_write) == 0 or int(doc_id) != int(doc_id_list_to_write[-1]):
                doc_id_list_to_write.append(doc_id)

        token_to_write = curr_token

    # write remaining things to disk
    if len(doc_id_list_to_write) > 0:
        skip_ptr_list = build_skip_list(doc_id_list_to_write)
        final_posting_lst_to_write = token_to_write + " " + " ".join(skip_ptr_list) + "\n"
        final_token_docid_list_to_write.append(final_posting_lst_to_write)
        final_token_offset_pair_to_write.append(token_to_write  + " " + str(posting_line_offset) + "\n")

    write_file_to_disk(out_postings, "".join(final_token_docid_list_to_write), posting_file_ptr, True)
    write_file_to_disk(out_dict, "".join(final_token_offset_pair_to_write), dict_file_ptr, True)


# returns a list of strings seperated by ' '
# [doc_id|skip_ptr doc_id doc_id doc_id|skip_ptr]
# if len(skip_ptr_list.split("|") == 2), skip pointer exists for that doc_id
def build_skip_list(posting_list):
    skip_ptr_list = []
    jump = ceil(sqrt(len(posting_list)))
    for idx, posting in enumerate(posting_list):
        if idx % jump == 0 and (idx + jump) < len(posting_list):
            next_val = posting_list[idx + jump]
            skip_ptr_list.append(posting + "|" + next_val)
        else:
            skip_ptr_list.append(posting)
    
    return skip_ptr_list


# https://stackoverflow.com/questions/40205223/priority-queue-with-tuples-and-dicts
class QueueEntry:
    def __init__(self, line, block_num):
        self.block_num = block_num
        self.token = line.split(" ")[0]
        self.posting_list = line.split(" ")[1:]

    def get_token(self):
        return self.token
    
    def get_block_num(self):
        return int(self.block_num)
    
    def get_posting_list(self):
        return self.posting_list
    
    def __eq__(self, other):
        return ((self.token, int(self.block_num)) == (other.get_token(), other.get_block_num()))
    
    def __lt__(self, other):
        return ((self.token, int(self.block_num)) < (other.get_token(), other.get_block_num()))


# Functions to read from disk
# file: path to file to be read
# offset: what offset to start reading from
# file_ptr: pointer to the file to be read, if exists
# num_lines: number of lines to be read
def read_from_file(file, offset = None, file_ptr = None, num_lines = 1):
    # open the file in read mode
    if file_ptr == None:
        file_ptr = open(file, 'r')
    
    # read all lines
    if offset == None:
        return file_ptr.readlines()
    
    file_ptr.seek(offset)
    if num_lines == 1:
        return file_ptr.readline()
    lines = []
    for i in range(num_lines):
        new_line = file_ptr.readline()
        # file ended before we read num_lines number of lines
        if len(new_line.strip()) == 0:
            break
        lines.append(new_line)
    return lines 


# Functions to write to disk
def write_block_to_disk(curr_block, posting_list, dictionary):
    result = ""
    # for every token in the dictionary
    for term in sorted(dictionary):
        result += term + " "
        # obtain the posting list, convert it to string and seperate by a whitespace " "
        result += " ".join([str(doc_id) for doc_id in posting_list[term]])
        result += "\n"
    # create a new spimi_block.txt file and write to it
    write_file_to_disk(BLOCKS_DIR + str(curr_block) + '.txt', result)


# writes the given file to the disk
# file_dir: path to file to be read
# content: text to write
# file_ptr: pointer to the file to be read, if exists
# is_append: open file in append or write mode
def write_file_to_disk(file_dir, content, file_ptr = None, is_append = False):
    # create a new file in append mode
    if is_append and file_ptr == None:
        file_ptr = open(file_dir, 'a')
    # create a new file to write to it
    elif not is_append and file_ptr == None:
        file_ptr = open(file_dir, 'w+')

    # write the content to the file
    file_ptr.write(content)
    

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    # in_dir = "/Users/nltk_data/corpora/reuters/training/"

    stemmer = PorterStemmer()
    dictionary = set()
    posting_list = {}

    block_index = 0
    num_lines_read = 0
    
    reset_dir(out_dict, out_postings)
    
    # pre-sort the docids so we can append to posting list directly
    doc_ids = [int(doc_id) for doc_id in os.listdir(in_dir)]
    doc_ids = sorted(doc_ids)

    start_time = time.perf_counter()
    # construction of dictionary and posting list
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

                    # one word read
                    num_lines_read += 1

                    # update the memory with the token and doc_id
                    if word not in dictionary:
                        dictionary.add(word)
                        posting_list[word] = [doc_id]
                    if doc_id not in posting_list[word]:
                        posting_list[word].append(doc_id)

                    # memory capacity achieved
                    if num_lines_read == BLOCK_SIZE:
                        write_block_to_disk(block_index, posting_list, dictionary)
                        # clear memory for next block
                        block_index += 1
                        num_lines_read = 0
                        dictionary = set()
                        posting_list = {}
    
    
    # write remaining information in the memory to the disk
    if num_lines_read > 0:
        write_block_to_disk(block_index, posting_list, dictionary)
        block_index += 1

    # merge all blocks together
    n_merge_blocks(block_index, out_dict, out_postings)

    # write list of doc_ids
    doc_id_result = ";".join([str(doc_id) for doc_id in doc_ids])    
    write_file_to_disk('doc_ids.txt', doc_id_result)

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
