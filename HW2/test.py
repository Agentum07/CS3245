#!/usr/bin/python3
import re
from nltk import sent_tokenize, word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk import sent_tokenize, word_tokenize

word = "can't"
word = re.sub(r'[^\w\s()]', '', word)
stemmer = PorterStemmer()
word = stemmer.stem(word=word.lower())
print(word_tokenize(word))