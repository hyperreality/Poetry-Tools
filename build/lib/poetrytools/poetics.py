#!/usr/bin/env python
#-*- coding: utf-8 -*-

# Tools for working with poems
#
# Licensed under GPLv2 or later.

from __future__ import print_function
import json, os, re, string, sys
from collections import defaultdict
from Levenshtein import distance
from .countsyl import count_syllables

with open(os.path.join(os.path.dirname(__file__), 'cmudict/cmudict.json')) as json_file:
    cmu = json.load(json_file)

not_in_cmu = []

def elided_d(word):
    if word[-2:] == "'d":
        return word[:-2] + "ed"
    return word

def tokenize(poem):
    tokens = []
    for line in open(poem).readlines():
        line = line.replace('-', ' ') 
        no_hyphens = line.replace('—', ' ') 
        cleaned = re.sub(r'[^0-9a-zA-Z\s\']', '', no_hyphens) # keep apostrophes
        tokens.append([elided_d(word) for word in cleaned.strip().split(' ')])
    return tokens

def stress(word):
    if word.lower() in not_in_cmu:
        return '1' + '0' * (count_syllables(word) - 1)
    elif word.lower() not in cmu:
        not_in_cmu.append(word.lower())
        return '1' + '0' * (count_syllables(word) - 1) # provisional logic for adding stress is to stress first syllable only
    else:
        pronunciation_string = str(''.join([a for a in min(cmu[word.lower()])]))
        stress_numbers = ''.join([x.replace('2', '1') for x in list(pronunciation_string) if x.isdigit()]) # not interested in secondary stress
        return stress_numbers   

def scanscion(poem):
    line_stresses = []
    currline = 0

    for line in poem:
        line_stresses.append([])
        [line_stresses[currline].append(stress(word)) for word in line if word]
        currline += 1

    return line_stresses

def rhymes(w1, w2, level=2):
     if w1.lower() in not_in_cmu or w2.lower() in not_in_cmu:
         return -1
     try:
         syllables = [' '.join([str(c) for c in lst]) for lst in cmu[w1.lower()]]
     except KeyError:
         not_in_cmu.append(w1.lower())
         return -1
     try:
         syllables2 = [' '.join([str(c) for c in lst]) for lst in cmu[w2.lower()]]
     except KeyError:
         not_in_cmu.append(w2.lower())
         return -1
     for syllable in syllables:
         for syllable2 in syllables2:
             if syllable2[-level:] == syllable[-level:]:
                 return 1
             else:
                 return 0

def rhyme_scheme(poem):
    last_words = [s[-1] for s in poem if s]
    scheme = ['x'] * len(last_words)

    # should dynamically GENERATE rhymenotation according to poem size
    rhyme_notation = list(string.ascii_uppercase)
#    for i in string.ascii_uppercase:
#        for j in string.ascii_lowercase:
#            rhymenotation.append(i+j) # add 676 more ways of notating rhyme for long poems

    currline = currrhyme = 0
    for word in last_words:
        rhymed = False
        for i in range(currline + 1,len(last_words)):
            if scheme[i] == 'x': # if word is not already part of a rhyme scheme
                if not word:
                    scheme[currline] = ' '
                elif rhymes(word, last_words[i], 2):                    
                    scheme[currline] = scheme[i] = rhyme_notation[currrhyme]
                    rhymed = True
        if rhymed == True:
            currrhyme += 1
        currline += 1

    return scheme

def guess_metre(poem):
    joined = [''.join(line) for line in scanscion(poem) if line]
    line_lengths = [len(line) for line in joined]
    num_lines = len(joined)

    possible_metres = {'iambic trimeter': '010101', 'iambic tetrameter': '01010101', 'iambic pentameter': '0101010101', 'trochaic tetrameter': '10101010', 'trochaic pentameter': '1010101010'}
    
    z = defaultdict(int)
    for line in joined:
    	for v in possible_metres.items():
            leven = distance(line,v[1])
            z[v[0]] += leven
    guessed_metre = min(z, key=z.get) # Minimum Levenshtein selected as best metrical match.
    return joined, num_lines, line_lengths, guessed_metre

def guess_rhyme_type(poem):
    joined = ''.join([l for l in rhyme_scheme(poem)])
    num_lines = len(joined)

    possible_rhyme_types = {'heroic couplet': 'AABB CCDD EEFF', 'alternate rhyme': 'ABAB CDCD EFEF GHGH', 'enclosed rhyme': 'ABBA CDDC EFFE', 'rima': 'ABABCBCDC', 'shakespearean sonnet': 'ABABCDCDEFEFGG', 'limerick': 'AABBA', 'no rhyme': 'xxxxxx'}

    z = defaultdict(int)
    for v in possible_rhyme_types.items():
        expanded = (v[1] * (num_lines/len(v[1])+1))[:num_lines]
        leven = distance(joined,expanded)
        z[v[0]] += leven
    guessed_rhyme = min(z, key=z.get) # Minimum Levenshtein selected as best metrical match.
    return joined, guessed_rhyme

def guess_form(poem, verbose=False):
    poem = tokenize(poem)

    def within_ranges(line_properties, ranges):
        if all([ranges[i][0] <= line_properties[i] <= ranges[i][1] for i in range(len(ranges))]):
            return True

    rhyme_scheme_string, rhyme = guess_rhyme_type(poem)
    metrical_scheme_string, num_lines, line_lengths, metre = guess_metre(poem)

    if verbose == True:
        print(metrical_scheme_string)
        print(rhyme + " (" + rhyme_scheme_string + ") + " + metre + " = ", end="")

    if within_ranges(line_lengths,[(4,6)*3]):
        return 'haiku'

    if line_lengths == [1,2,3,4,10]:
        return 'tetractys'

    if num_lines == 5:
        if within_ranges(line_lengths,[(8,11),(8,11),(5,7),(5,7),(8,11)]):
            return 'limerick'

        if within_ranges(line_lengths,[(4,6),(6,8),(4,6),(6,8),(6,8)]):
            return 'tanka'

        if rhyme == 'no rhyme':
            return 'cinquain'

    if num_lines == 8:
        if within_ranges(line_lengths,[(10,12)*11]) and rhyme == 'rima':
            return 'ottava rima'

    if num_lines == 14:
        if metre == 'iambic pentameter' and rhyme == 'shakespearean sonnet' or rhyme == 'alternate rhyme':
            return 'Shakespearean sonnet'
        return 'sonnet with ' + metre + ' or irregular meter'
    
    if rhyme == 'no rhyme' and metre == 'iambic pentameter':
        return 'blank verse'

    return '???' 

if __name__ == '__main__':
    print(guess_form(sys.argv[1], verbose=True))
    if not_in_cmu:
        print("not in CMU dictionary: " + ', '.join([word for word in not_in_cmu]))