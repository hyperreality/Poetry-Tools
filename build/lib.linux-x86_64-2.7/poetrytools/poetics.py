#!/usr/bin/env python
#-*- coding: utf-8 -*-

# Tools for working with poems
#
# Licensed under GPLv2 or later.

from __future__ import print_function
import json, os, re, sys
from collections import defaultdict
from string import ascii_lowercase
from Levenshtein import distance
from .countsyl import count_syllables

try:
    from nltk.corpus import cmudict
    cmu = cmudict.dict()
except:
    with open(os.path.join(os.path.dirname(__file__), 'cmudict/cmudict.json')) as json_file:
        cmu = json.load(json_file)

not_in_cmu = []

def elided_d(word):
    if word[ - 2 : ] == "'d":
        return word[ : - 2] + "ed"
    return word

def tokenize(poem):
    tokens = []
    for line in poem.split('\n'):
        line       = line.replace('-', ' ') 
        no_hyphens = line.replace('—', ' ') 
        cleaned    = re.sub(r'[^0-9a-zA-Z\s\']', '', no_hyphens) # keep apostrophes
        tokens.append([elided_d(word) for word in cleaned.strip().split(' ')])
    return tokens

def stress(word):
    if word.lower() in not_in_cmu or word.lower() not in cmu:
        not_in_cmu.append(word.lower())
        return '1' + '0' * (count_syllables(word) - 1) # provisional logic for adding stress is to stress first syllable only
    else:
        pronunciation_string = str(''.join([a for a in min(cmu[word.lower()])]))
        stress_numbers       = ''.join([x.replace('2', '1') for x in list(pronunciation_string) if x.isdigit()]) # not interested in secondary stress
        return stress_numbers   

def scanscion(poem):
    poem = tokenize(poem)

    line_stresses = []
    currline      = 0

    for line in poem:
        line_stresses.append([])
        [line_stresses[currline].append(stress(word)) for word in line if word]
        currline += 1

    return line_stresses

def rhymes(w1, w2, level = 2):
     if w1.lower() in not_in_cmu or w2.lower() in not_in_cmu:
         return - 1
     try:
         syllables = [' '.join([str(c) for c in lst]) for lst in cmu[w1.lower()]]
     except KeyError:
         not_in_cmu.append(w1.lower())
         return - 1
     try:
         syllables2 = [' '.join([str(c) for c in lst]) for lst in cmu[w2.lower()]]
     except KeyError:
         not_in_cmu.append(w2.lower())
         return - 1
     for syllable in syllables:
         for syllable2 in syllables2:
             if syllable2[ - level : ] == syllable[ - level : ]:
                 return 1
             else:
                 return 0

def rhyme_scheme(poem):
    poem = tokenize(poem)

    last_words = [s[ - 1] for s in poem if s]
    scheme     = ['X'] * len(last_words)

    rhyme_notation = list(ascii_lowercase)

    currline = currrhyme = 0
    for word in last_words:
        rhymed = False
        for i in range(currline + 1, len(last_words)):
            if scheme[i] == 'X' : # if word is not already part of a rhyme scheme
                if not word:
                    scheme[currline] = ' '
                elif rhymes(word, last_words[i], 2):                    
                    scheme[currline] = scheme[i] = rhyme_notation[currrhyme]
                    rhymed           = True
        if rhymed == True:
            currrhyme += 1
        currline += 1
   
    # find duplicate lines, important for some forms like rondeau
    D = defaultdict(list)
    for lineno, line in enumerate(poem):
        D[tuple(line)].append(lineno)
    duplicates = {
                   k : v for k,
                   v in D.items() if len(k) > 1 and len(v) > 1}  
    for num in sorted(duplicates.values()):
        for n in num:
            scheme[n] = scheme[n].upper()

    return scheme

def guess_metre(poem):
    joined       = [''.join(line) for line in scanscion(poem) if line]
    line_lengths = [len(line) for line in joined]
    num_lines    = len(joined)

    possible_metres = {
                        'iambic trimeter'     : '010101',
                        'iambic tetrameter'   : '01010101',
                        'iambic pentameter'   : '0101010101',
                        'trochaic tetrameter' : '10101010',
                        'trochaic pentameter' : '1010101010'}

    z = defaultdict(int)
    for line in joined:
        for v in possible_metres.items():
            leven = distance(line, v[1])
            z[v[0]] += leven
    guessed_metre = min(z, key = z.get) # Minimum Levenshtein selected as best metrical match.
    return joined, num_lines, line_lengths, guessed_metre

def guess_rhyme_type(poem):
    joined    = ''.join([l for l in rhyme_scheme(poem)])
    num_lines = len(joined)

    possible_rhyme_types = {
                             'couplets'             : 'aabb ccdd eeff',
                             'alternate rhyme'      : 'abab cdcd efef ghgh',
                             'enclosed rhyme'       : 'abba cddc effe',
                             'rima'                 : 'ababcbcdc',
                             'shakespearean sonnet' : 'ababcdcdefefgg',
                             'limerick'             : 'aabba',
                             'no rhyme'             : 'XXXXX'}

    z = defaultdict(int)
    for v in possible_rhyme_types.items():
        expanded = (v[1] * (num_lines // len(v[1]) + 1))[ : num_lines]
        leven    = distance(joined, expanded)
        z[v[0]] += leven
    guessed_rhyme = min(z, key = z.get) # Minimum Levenshtein selected as best metrical match.
    return joined, guessed_rhyme

def guess_form(poem, verbose = False):
    def within_ranges(line_properties, ranges):
        if all([ranges[i][0] <= line_properties[i] <= ranges[i][1] for i in range(len(ranges))]):
            return True

    rhyme_scheme_string, rhyme                             = guess_rhyme_type(poem)
    metrical_scheme_string, num_lines, line_lengths, metre = guess_metre(poem)

    if verbose == True:
        print(metrical_scheme_string)
        print(rhyme + " (" + rhyme_scheme_string + ") + " + metre + " = ", end = "")

    if num_lines == 3 and within_ranges(line_lengths, [(4, 6), (6, 8), (4, 6)]):
        return 'haiku'

    if num_lines == 5:
        if line_lengths == [1, 2, 3, 4, 10]:
            return 'tetractys'

        if within_ranges(line_lengths, [(8, 11), (8, 11), (5, 7), (5, 7), (8, 11)]):
            return 'limerick'

        if within_ranges(line_lengths, [(4, 6), (6, 8), (4, 6), (6, 8), (6, 8)]):
            return 'tanka'

        if rhyme == 'no rhyme':
            return 'cinquain'

    if num_lines == 8:
        if within_ranges(line_lengths, [(10, 12) * 11]) and rhyme == 'rima':
            return 'ottava rima'

    if num_lines == 14:
        if metre == 'iambic pentameter' and rhyme == 'shakespearean sonnet' or rhyme == 'alternate rhyme':
            return 'Shakespearean sonnet'
        return 'sonnet with ' + metre + ' or irregular meter'

    if rhyme == 'couplets' and metre == 'iambic pentameter':
        return 'heroic couplets'

    if metre == 'iambic pentameter':
        return 'blank verse'

    return '???' 

if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        guess_form(f.read())
    if not_in_cmu:
        print("not in CMU dictionary: " + ', '.join([word for word in not_in_cmu]))