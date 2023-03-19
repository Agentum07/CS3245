This is the README file for A0000000X's submission
Email(s): e0000000@u.nus.edu

== Python Version ==

I'm using Python Version 3.8.10 for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

index.py:
1. The directory is reset: any existing dictionary.txt, posting.txt, bsbi_block files are deleted.
2. Files are read in ascending order of their document ids. 1.txt is read before 5.txt 
3. For each file in order to collect the vocabulary, tokenization, case-folding and stemming is applied on the document text.
4. Scalable index construction:
I have implemented SPIMI in this project. I set the memory limit as 120,000. (Just wanted to have 10 doc files on the nltk corpora)
The tokens are stored in a set data structure. Posting lists are stored in a dictionary data structure (token -> list of docIDs)
Once the memory limit is reached, the current posting list is written to the disk in sorted order. I only write the posting list because
a dictionary can be obtained from the posting list, but not the other way around. These blocks are written in a new directory called 'spimi_blocks'
Each line contains the posting list for 1 token.
Once the block is written, the memory is cleared for the next block.

Once all the blocks have been written, I perform n-way merge, where n = total number of blocks.
The idea of the merge has been taken from stack overflow, corresponding link has been tagged.

Merge algorithm:
Open all block files and read the first 'k' lines from each file. k = 120,000 / number of blocks.
Create a priority queue and queue items based on 
  1. The token. 'ab' is added after 'a'
  2. The block number. same token from block2 is added after token from block1.
Run through the priority queue and keep writing to the files - dictionary.txt and posting.txt. 

The priority queue contains an object of the class QueueItem. Taken from stack-overflow, I created this class to be able to a tuple of
(string, int). Relevant link is in the code.
With that, indexing comes to an end.

5. Skip pointer creation.
Skip pointers are created and stored in the posting.txt.
They are placed at even intervals of math.ceil(math.sqrt(len(posting_list)))
If a docID has a skip pointer, it is written to posting.txt as "doc_ID|skip". normal docIDs are written like "docID "
This is done because => to obtain the individual doc_ids, I can split by " ".
To obtain the skip, I can split by "|" then read the 2nd value.
Final posting.txt looks like: [token] [docID|skip] [docID] [docID] and so on 

I also write the sorted list of all doc_ids in the file 'doc_ids.txt'. This is needed for search queries.

search.py 
queries are parsed and evaluated together. I am aware that this violates SRP and do have a workaround for it, but I didn't have the
time to implement the workaround. I will explain my current approach, then the workaround I planned on implementing.
Current approach:
The query is tokenized, stemmed then case-folding is applied.
The query_token can be 2 things => a token, an operator (and, or, not, left_bracket, right_bracket)
The core logic is, every token is considered to be attached to the closest operator. 
The query is converted from op1 OPERATOR1 op2 OPERATOR2 op3 to OPERATOR1 op1 OPERATOR1 op2 OPERATOR2 op3. This allows me to add the first
token to the corresponding set as well.
Every token is either an "and" operand or an "or" operand.
" AND B", means B is an AND, and so it gets added to the set of all "and" operands. Similarly for "OR" operands.
The 2 types of operators are maintained at sets called "ands" and "ors"
For "NOT" operator, the token is still considered to be an "AND" or "OR" operand, by using booleans.
For the first 
The ands and ors set:
For every operand, the corresponding posting list is calculated. This posting list is added to set. I chose a set because it cannot have
duplicate values and is fast. A query of the form "A AND A AND A" will result in the intermediate posting list of "A" once.

The query goes from "A OR B AND C OR D AND E" to "AND C AND E OR A OR B OR D".
Once the query has been parsed fully, it is time to combine all ands and ors individually. This is done using intersection and union 
operations, both of which have been coded.

Intersection:
So the posting list read from the disk is a tuple of tuples: ((doc_id1, skip_pointer1), (doc_id2, skip_pointer2)...)
if a skip_pointer does not exist, the value is -1.
Once 2 ands are merged, I reconstruct the skip pointer list.
Once the query evaluation is complete and we merge the "ands" together, they are first sorted in increasing order of lengths to reduce
computation as discussed in the lecture.
Union:
Ors are just added on its own.

"A OR B AND C OR D AND E" => "AND C AND E OR A OR B OR D" => "AND F OR G"
Now we have 2 lists, the final_ands (after intersection of intermediate ands) and final_ors (after union of intermediate ors)
Based on the operator in the middle, I either intersect or take union.

Nested queries:
My code works for 1 level of nesting.
If I encounter a left bracket, I iterate through till I find the right bracket, and pass the query[left_bracket: right_bracket]
to my function as a new query again.

Then I write the result to the output file.

Misc:
The workaround to not parse and evaluate together:
I planned on creating a QueryToken class. 
This class would have 4 fields: token, posting_list, posting_list_size, operand (and, or, not)
Once the query has been parsed and all QueryTokens have been generated, I can sort them on the basis of posting_list_size 
and merge.
Unfortunately I was unable to do this due to other commitments.

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.
index.py: creates the index for the corpora and saves in the disk. Creates 3 files: dictionary.txt, posting.txt and doc_ids.txt
search.py: evaluates queries given in queries.txt and writes the result to output.txt
readME.txt: explanation of the algorithm and self-declaration
essay.txt: my responses to the essay questions
dictionary.txt: the sorted dictionary created after indexing
posting.txt: the posting list created after indexing
doc_ids.txt: file containing all doc_ids in sorted order, seperated by a semi-colon
== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I, A0226594W, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0226594W, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

I suggest that I should be graded as follows:
Any code I have taken from a website has been tagged.
The logic is mine, I have spent ~25 hours on this assignment.
I have only consulted stack overflow for python help, link to non-trivial implementations has been 
provided in the code base and the references as well.


== References ==

3 stack overflow websites:
1. https://stackoverflow.com/questions/40205223/priority-queue-with-tuples-and-dicts
2. https://stackoverflow.com/questions/4056768/how-to-declare-array-of-zeros-in-python-or-an-array-of-a-certain-size
3. https://stackoverflow.com/questions/5055909/algorithm-for-n-way-merge