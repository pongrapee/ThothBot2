# -*- coding: utf-8 -*-
# coding='utf-8'


#!/usr/bin/env python
# 
# Copyright 2010  Niniane Wang (niniane@gmail.com)
# Reviewed by Alex Mendes da Costa.
# 
# This is a simple Tf-idf library.  The algorithm is described in
#   http://en.wikipedia.org/wiki/Tf-idf
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__author__ = "Niniane Wang"
__email__ = "niniane at gmail dot com"

import math
import re
from operator import itemgetter

DEBUG = False

class TfIdf:

  """Tf-idf class implementing http://en.wikipedia.org/wiki/Tf-idf.
  
	 The library constructs an IDF corpus and stopword list either from
	 documents specified by the client, or by reading from input files.  It
	 computes IDF for a specified term based on the corpus, or generates
	 keywords ordered by tf-idf for a specified document.
  """

  def __init__(self, corpus_filename = None, stopword_filename = None,
			   DEFAULT_IDF = 1.5):
	"""Initialize the idf dictionary.  
	
	   If a corpus file is supplied, reads the idf dictionary from it, in the
	   format of:
		 # of total documents
		 term: # of documents containing the term

	   If a stopword file is specified, reads the stopword list from it, in
	   the format of one stopword per line.

	   The DEFAULT_IDF value is returned when a query term is not found in the
	   idf corpus.
	"""
	self.num_docs = 0
	self.term_num_docs = {}     # term : num_docs_containing_term
	self.stopwords = []
	self.idf_default = DEFAULT_IDF

	if corpus_filename:
		files = []
		if isinstance(corpus_filename, (list)):
			files = corpus_filename
		else:
			files = [corpus_filename]

		for file_name in files:
			if DEBUG: print file_name
			try:
				corpus_file = open(file_name, "r")
			except Exception as e:
				print "file",file_name,"not found"
				return
			# Load number of documents.
			line = corpus_file.readline()
			try:
				self.num_docs = int(line.strip())
			except:
				self.num_docs = 0
			# Reads "term:frequency" from each subsequent line in the file.
			for line in corpus_file:
				tokens = line.rpartition(":")
				term = tokens[0].strip()
				frequency = int(tokens[2].strip())
				if term in self.term_num_docs:
					self.term_num_docs[term] = self.term_num_docs[term] + frequency
				else:
					self.term_num_docs[term] = frequency
				
	if stopword_filename:
	  stopword_file = open(stopword_filename, "r")
	  self.stopwords = [line.strip() for line in stopword_file]
	
	#mainstopword_file = open('main_stop.txt', "r")
	#self.mainstopwords = [line.strip() for line in mainstopword_file]
	
  def get_tokens(self, str):
	#print str.lower()
	"""Break a string into tokens, preserving URL tags as an entire token.

	   This implementation does not preserve case.  
	   Clients may wish to override this behavior with their own tokenization.
	"""
	result = str.lower().replace('\r',' ').replace('\n',' ').replace('\t',' ').replace('"',' ').replace("'",' ').replace('(',' ').replace(')',' ').split(" ")
	result = filter(None, result)
	for item in result:
		if item.strip() == '':
			result.remove(item)
	
	result2= []
	for item in result:
		result2.append(item)
	
	do_bigram_trigram = True
	if do_bigram_trigram == True:
		if len(result) >= 2:
			for i in range(len(result)-1):
				temp = result[i]+result[i+1]
				if ((len(result[i])<=10 or len(result[i+1])<=10) and len(temp) <= 25):
					if ((re.search(ur'[a-zA-Z]',temp,re.U) == None) or re.search(ur'[\u0E00-\u0E7F]',temp.decode('utf-8','ignore'),re.U) == None) and (re.search(ur'[!@#$%^&*()_+-=\\/|{}\[\]<>,\.\?]',temp,re.U) == None):
						result2.append(temp)
						
		if len(result) >= 3:
			for i in range(len(result)-2):
				temp = result[i]+result[i+1]+result[i+2]
				if ((len(result[i])<=7 or len(result[i+1])<=7 or len(result[i+2])<=7) and len(temp) <= 25):
					if ((re.search(ur'[a-zA-Z]',temp,re.U) == None) or re.search(ur'[\u0E00-\u0E7F]',temp.decode('utf-8','ignore'),re.U) == None) and (re.search(ur'[!@#$%^&*()_+-=\\/|{}\[\]<>,\.\?]',temp,re.U) == None):
						result2.append(temp)
		
		# if len(result) >= 4:
			# for i in range(len(result)-3):
				# temp = result[i]+result[i+1]+result[i+2]+result[i+3]
				# if ((len(result[i])<=3 or len(result[i+1])<=3 or len(result[i+2])<=3 or len(result[i+3])<=3) and len(temp) <= 15):
					# if ((re.search(u'[a-zA-Z]',temp,re.U) == None) or re.search(u'[ก-ฮ]',temp,re.U) == None) and (re.search(u'[\!@#$%^&\*()_\+\-\?\\\/\.\,:;]',temp,re.U) == None):
						# result2.append(temp)
	return result2
	
  def add_input_document(self, input):
	"""Add terms in the specified document to the idf dictionary."""
	self.num_docs += 1
	words = set(self.get_tokens(input))
	for word in words:
	  if word in self.term_num_docs:
		self.term_num_docs[word] += 1
	  else:
		self.term_num_docs[word] = 1

  def save_corpus_to_file(self, idf_filename, stopword_filename,
						  STOPWORD_PERCENTAGE_THRESHOLD = 0.05, find_diff_only = False):
	"""Save the idf dictionary and stopword list to the specified file."""
	if not self.term_num_docs:
		return

	output_file = open(idf_filename, "w")

	output_file.write(str(self.num_docs) + "\n")
	for term, num_docs in sorted(self.term_num_docs.items(),key=lambda x:x[1],reverse=True):
	  output_file.write(term + ": " + str(num_docs) + "\n")
	  #print term.decode('utf-8','ignore').encode('tis-620','ignore')

	sorted_terms = sorted(self.term_num_docs.items(), key=itemgetter(1),
						  reverse=True)
	stopword_file = open(stopword_filename, "w")
	
	for term, num_docs in sorted_terms:
	  if num_docs < STOPWORD_PERCENTAGE_THRESHOLD * self.num_docs:
		break
	  if not find_diff_only:
	  	stopword_file.write(term + "\n")
	  else:
	  	if term not in self.stopwords:
	  		stopword_file.write(term + "\n")

  def get_num_docs(self):
	"""Return the total number of documents in the IDF corpus."""
	return self.num_docs

  def get_idf(self, term):
	"""Retrieve the IDF for the specified term. 
	
	   This is computed by taking the logarithm of ( 
	   (number of documents in corpus) divided by (number of documents
		containing this term) ).
	 """
	if term in self.stopwords:
	  return 0
	  
	#if term in self.mainstopwords:
	#  return 0
	  
	if not term in self.term_num_docs:
	  return self.idf_default

	return math.log(float(1 + self.get_num_docs()) / 
	  (1 + self.term_num_docs[term]))

  def get_doc_keywords(self, curr_doc):
	"""Retrieve terms and corresponding tf-idf for the specified document.

	   The returned terms are ordered by decreasing tf-idf.
	"""
	tfidf = {}
	tokens = self.get_tokens(curr_doc)
	tokens_set = set(tokens)
	for word in tokens_set:
	  # The definition of TF specifies the denominator as the count of terms
	  # within the document, but for short documents, I've found heuristically
	  # that sometimes len(tokens_set) yields more intuitive results.
	  #if word not in self.stopwords:
		mytf = float(tokens.count(word)) / len(tokens)
		myidf = self.get_idf(word)
		myrank = mytf * myidf
		if myrank > 0 and len(word) >= 2 and tokens.count(word) >= 1:
			tfidf[word] = myrank
		
	
	return sorted(tfidf.items(), key=itemgetter(1), reverse=True)
