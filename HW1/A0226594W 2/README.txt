This is the README file for A0226594W's submission
Email: e0638880@u.nus.edu

== Python Version ==

I'm using Python Version <3.8.10> for
this assignment.

== General Notes about this assignment ==

Give an overview of your program, describe the important algorithms/steps 
in your program, and discuss your experiments in general.  A few paragraphs 
are usually sufficient.

Program Overview:
Build_LM -
The code is adapted up from W1 lecture slides, namely slides 21 and 22.
I have put relevant comments in the code.
We add the start and end tokens. I have chosen '{' and '}' for start and end respectively. 
This is because no language uses this character. These tokens did not help computation, but I think
it's good practice to have start and end tokens so I kept them anyway.

First, we extract the 4grams in Build_LM function. Using the language tag, we retrieve the specific
dictionary to store the counts for all 4grams. Basically, the first letter of all train input is the language 
(i = indonesian, t = tamil, m = malaysian) and so I return the corresponding dictionary.
The dictionary is then populated by the 4 gram counts.
Now, we have the vocabulary for all 3 languages.
For add-one smoothing, we need to add all vocabulary from the other languages.
So, for dict A, we need the vocabularies in (B - A) and (C - A). The function combine_dicts does just that.
Now, we have the entire vocabulary for all 3 languages, but some counts are 0. We perform add-one smoothing.
Now, we convert the counts to probabilities and then take the log. We take log because the vocabulary is too big and 
probabilities are close to 0.
We then return the probability dictionaries for each language.

Test_LM -
We extract the test string and convert into 4gram.
We then refer to the language probability dictionaries. Since we have taken the log of the probabilities, we just add the values
instead of multiplying them.
We then predict the language with the highest probability as the probability.
Classification of "other":
When the probability of all languages is 0, no part of the phrase has never been seen before. Which means that it is a new 
language, and is classified as others.
I could have created a threshold value to classify others as discussed on piazza, but I fear that would cause overfitting.
We write the predicted language and text in an output file.

This concludes the program.

== Files included with this submission ==

List the files in your submission here and provide a short 1 line
description of each file.  Make sure your submission's files are named
and formatted correctly.
build_test_LM.py: The language model.
essay.txt: Response to the essay questions
README.txt: Explanation of the code and integrity declaration

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I, A0226594W, certify that I have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I
expressly vow that I have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I, A0226594W, did not follow the class rules regarding homework
assignment, because of the following reason:

I suggest that I should be graded as follows:
Any code I have taken from a website has been tagged.
The logic is mine, I have only consulted stack overflow for python help, link to which has been 
provided in the code base and the references as well.
I had the idea of taking log of the probability before the piazza discussion, but I have no proof of it.
Rest of the code I have written is mine, I should be graded for all of it.

== References ==
for extracting 4grams: https://stackoverflow.com/a/69793069
