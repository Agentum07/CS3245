This is the README file for A0226594W's submission
Email(s): e0638880@u.nus.edu

== Python Version ==

I'm using Python Version 3.8.10 for this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

Indexing:
1. The directory is reset: any existing dictionary.txt, posting.txt, doc_lengths.txt files are deleted.
2. Files are read in ascending order of their document ids. 1.txt is read before 5.txt 
3. For every document, I calculate the frequency of each word in it. The posting list is a dictionary of dictionaries.
posting_list: {word => {doc_id => frequency}}
4. For every document, I calculate the document length as discussed on piazza.
5. Once all documents have been read and processed, I convert all word frequencies to their tf values. (1 + log(freq))
6. I then flatten my posting_list to become of the form {word => (doc_id, tf)}
7. I write the posting_list and doc_lengths to memory using pickle. I also create a dictionary which stores the word => offset for the posting list. 
I have used in-memory indexing using Pickle for on disk persistence.

Querying:
1. The dictionary and doc_lengths are loaded from pickle.
2. All query terms are tokenization, stemmed, case folding
3. For all terms in the query, the term weight is calculated.
4. For every token, posting list is retrieved
5. The document frequency and idf is calculated
6. The score for the document id is calculated
7. The score is then normalized.
8. The top 10 values are then returned
== Files included with this submission ==

index.py => for the indexing phase
search.py => for the querying 
util.py => contains all the utility functions 
dictionary.txt => binary data for the dictionary
posting_list.txt => binary data for the posting list
List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I, A0226594W, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

I have written all this code myself. Any code I have taken from an external source has been tagged.
I have spent ~15 hours on this assignemnt.

== References ==
https://stackoverflow.com/questions/7197315/5-maximum-values-in-a-python-dictionary
https://stackoverflow.com/questions/9047364/how-to-check-for-a-key-in-a-defaultdict-without-updating-the-dictionary-python