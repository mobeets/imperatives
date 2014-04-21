#!/usr/bin/env python
# encoding=utf-8

import re
import random
import argparse

# http://www.clips.ua.ac.be/pages/pattern-en
from pattern.en import wordnet, conjugate, pluralize, singularize, quantify
from pattern.en.wordlist import BASIC

singled_if_word = lambda x: singularize(x) if wordnet.synsets(singularize(x)) else None
singled_if_word_2 = lambda x: x[:-1] if wordnet.synsets(x[:-1]) else None

SOURCE = 2
if SOURCE == 0:
	NOUNS = wordnet.NOUNS.keys()
	VERBS = wordnet.VERBS.keys()
	ADJS = wordnet.ADJECTIVES.keys()
elif SOURCE == 1:
	basic_words = lambda pos: [w for w in BASIC if wordnet.synsets(w, pos=pos)]
	NOUNS = basic_words('NN')
	VERBS = basic_words('VB')
	ADJS = basic_words('JJ')
else:
	# http://dictionary-thesaurus.com/wordlists.html
	load = lambda filename: [w.lower().strip() for w in open(filename).read().split('\n') if w.lower().strip() and wordnet.synsets(w.lower().strip())]

	NOUNS = load('nouns.txt')
	NOUNS = [singled_if_word(x) if x.endswith('s') else x for x in NOUNS if not x.endswith('s') or singled_if_word(x)]

	VERBS = load('verbs.txt')
	ADJS = load('adjectives.txt')

A1 = ['start', 'stop']
A2 = ['always', 'never']
A3 = ['occasionally', 'constantly']
C = ['the', 'the', 'all those', 'so many']
C2 = ['the', 'the', 'all those']
coin_flip = lambda p: random.random() < p

def get_related_noun_or_not(noun, d=True):
	w = wordnet.synsets(noun)
	if w:
		w = w[0]
		w1 = w.hyponyms()
		w2 = w.hypernyms()
		if w1 + w2:
			nw = random.choice(w1 + w2)
			if nw and nw.senses:
				return nw.senses[0]
	elif wordnet.synsets(singularize(noun)) and d:
		return get_related_noun_or_not(singularize(noun, False))
	return noun

def random_imperative(noun=None):
	if noun:
		n = get_related_noun_or_not(noun)
	else:
		n = random.choice(NOUNS)
	v = random.choice(VERBS)
	c = ''

	if coin_flip(0.5):
		adj = random.choice(ADJS)
	else:
		adj = ''

	if coin_flip(0.7):
		n = pluralize(n)
		c = random.choice(C2)
	else:
		i = random.randint(1, 5)
		n = quantify(adj + ' ' + n, amount=i)
		adj = ''

	if coin_flip(0.25):
		a = ''
		v = conjugate(v)
	elif coin_flip(0.33):
		v = conjugate(v, 'part') # present participle
		a = random.choice(A1)
		c = random.choice(C)
	elif coin_flip(0.5):
		v = conjugate(v)
		a = random.choice(A2)
	else:
		v = conjugate(v)
		a = random.choice(A3)
	
	phrase = '{0} {1} {2} {3} {4}'.format(a, v, c, adj, n)
	phrase = phrase[1:] if phrase.startswith(' ') else phrase
	return re.sub(' +', ' ', phrase)

def add_qualifier(phrase):
	n = random.choice(NOUNS)
	v = random.choice(VERBS)

	if coin_flip(0.5):
		a = 'cannot'
	else:
		a = 'can'

	if coin_flip(0.5):
		b = 'of'
	else:
		b = 'for the'

	n = pluralize(n)
	v = conjugate(v)

	qual = '{0} you {1} {2}'.format(n, a, v)
	return '{0} {1} {2}'.format(phrase, b, qual)

def protect_against_plurals(word):
	wd = word
	if word.endswith('s'):
		wd = singled_if_word(word) if singled_if_word(word) else word
		if wd == word:
			wd = singled_if_word_2(word) if singled_if_word_2(word) else word
	return wd

def main(N=50, subject=None):
	if subject:
		subject = protect_against_plurals(subject)
	for _ in xrange(N):
		if coin_flip(0.5):
			imp = random_imperative(subject)
		else:
			imp = add_qualifier(random_imperative(subject))
		print imp.capitalize() + '.'

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--N", default=50, type=int, help="The number of imperatives to generate.")
parser.add_argument("--S", default=None, type=str, help="The related subject of the imperatives.")
args = parser.parse_args()

if __name__ == '__main__':
	main(args.N, args.S)
