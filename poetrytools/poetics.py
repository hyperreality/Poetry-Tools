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

# Import CMU dictionary
with open(os.path.join(os.path.dirname(__file__), 'cmudict/cmudict.json')) as json_file:
    cmu = json.load(json_file)

def tokenize(poem):
    """
    Simple tokenizer. Remove or replace unwanted characters, then parse to a list of lists of sentences and words
    """
    tokens = []

    # Characters to replace that might cause problems later on
    replacements = {'-': ' ', '—': ' ', '\'d': 'ed'}

    for original, replacement in replacements.iteritems():
        replaced = poem.replace(original, replacement)
    # Keep apostrophes and accented characters, discard everything else
    cleaned = re.sub(r'[^0-9a-zA-Z\u00E0-\u00FC\s\']', '', replaced) 

    for line in cleaned.split('\n'):
        tokens.append([word for word in line.strip().split(' ')])
    return tokens

def levenshtein(tocompare, candidates, linebyline=False):
    z = defaultdict(int)
    if linebyline == True:
        for line in tocompare:
            for v in candidates.items():
                z[v[0]] += distance(line, v[1])
    else:
        num_lines = len(tocompare)
        for v in candidates.items():
            expanded = (v[1] * (num_lines // len(v[1]) + 1))[:num_lines]
            z[v[0]] += distance(tocompare, expanded)
    best_guess = min(z, key = z.get)
    return best_guess

def stress(word):
    """
    Represent strong and weak stress of a word with a series of 1's and 0's
    """
    syllables = getSyllables(word)
    if syllables:
        # TODO: Find a better way to handle multiple pronunciations than just using the min
        min_syllables = min(syllables)
        pronunciation_string = str(''.join(min_syllables))
        stress_numbers       = ''.join([x.replace('2', '1') for x in pronunciation_string if x.isdigit()]) # not interested in secondary stress
        return stress_numbers
    else:
        # Provisional logic for adding stress when the word is not in the dictionary is to stress first syllable only
        return '1' + '0' * (count_syllables(word) - 1) 

def scanscion(poem):
    """
    Get stress notation for every line in the poem
    """
    line_stresses = []
    currline      = 0

    for line in poem:
        line_stresses.append([])
        [line_stresses[currline].append(stress(word)) for word in line if word]
        currline += 1

    return line_stresses

def getSyllables(word):
    """
    Look up a word in the CMU dictionary, return a list of syllables
    """

    try:
        return(cmu[word.lower()])
    except KeyError:
        return False

def rhymes(word1, word2, level=2):
    """
    For each word, get a list of various syllabic pronunications. Then check whether the last level number of syllables is pronounced the same. If so, the words probably rhyme
    """
    pronunciations = getSyllables(word1)
    pronunciations2 = getSyllables(word2)

    if pronunciations and pronunciations2:
        for syllable in pronunciations:
            for syllable2 in pronunciations2:
                if syllable2[-level:] == syllable[-level:]:
                    return True
    return False

def rhyme_scheme(poem):
    """
    Get a rhyme scheme for the poem. For each line, lookahead to the future lines of the poem and see whether last words rhyme.
    """
    scheme = ['X'] * len(poem)

    rhyme_notation = list(ascii_lowercase)

    currrhyme = 0

    for lineno in range(0, len(poem)):
        for futurelineno in range(lineno + 1, len(poem)):
            # if next line is not already part of a rhyme scheme
            if scheme[futurelineno] == 'X':
                if poem[lineno] == ['']:
                    # If blank line, represent that in the notation
                    scheme[lineno] = ' '
                elif rhymes(poem[lineno][-1], poem[futurelineno][-1]):
                    scheme[lineno] = scheme[futurelineno] = rhyme_notation[currrhyme]
                    currrhyme += 1

                    # Capitalise rhyme if the whole line is identical
                    if poem[lineno] == poem[futurelineno]:
                        scheme[lineno] = scheme[lineno].upper()
                        scheme[futurelineno] = scheme[futurelineno].upper()

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

    guessed_metre = levenshtein(joined, possible_metres, linebyline=True)
    return joined, num_lines, line_lengths, guessed_metre

def guess_rhyme_type(poem):
    joined    = ''.join([l for l in rhyme_scheme(poem)])

    possible_rhymes = {
                             'couplets'             : 'aabb ccdd eeff',
                             'alternate rhyme'      : 'abab cdcd efef ghgh',
                             'enclosed rhyme'       : 'abba cddc effe',
                             'rima'                 : 'ababcbcdcdedefefgfghg',
                             'rondeau rhyme'        : 'aabba aab C aabba C',
                             'shakespearean sonnet' : 'ababcdcdefefgg',
                             'limerick'             : 'aabba',
                             'no rhyme'             : 'XXXXX'}

    guessed_rhyme = levenshtein(joined, possible_rhymes, linebyline=False)
    return joined, guessed_rhyme

def stanza_lengths(rhymescheme):
    stanzas, j, inspace = [0], 0, False
    for i in rhymescheme:
        if i == ' ':
            if not inspace:
                j += 1;
                stanzas += [0];
                inspace = True
        else:
            stanzas[j] = stanzas[j] + 1;
            inspace = False
    joined = ','.join(map(str,stanzas)) + ","

    possible_stanzas = {
                             'sonnet'             : '14,',
                             'tercets'             : '3,'}

    guessed_stanza = levenshtein(joined, possible_stanzas, linebyline=False)
    return joined, guessed_stanza

def guess_form(poem, verbose=False):
    def within_ranges(line_properties, ranges):
        if all([ranges[i][0] <= line_properties[i] <= ranges[i][1] for i in range(len(ranges))]):
            return True

    poem = tokenize(poem)

    metrical_scheme, num_lines, line_lengths, metre = guess_metre(poem)
    rhyme_scheme_string, rhyme = guess_rhyme_type(poem)
    stanza_length_string, stanza = stanza_lengths(rhyme_scheme_string)

    if verbose == True:
        print("Metre: " + ' '.join(metrical_scheme))
        print("Rhyme scheme: " + rhyme_scheme_string)
        print("Stanza lengths: " + stanza_length_string)
        print()
        print("Closest metre: " + metre)
        print("Closest rhyme: " + rhyme)
        print("Closest stanza type: " + stanza)
        print("Guessed form: ",end="")

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

    if num_lines == 15:

        return 'rondeau'

    if rhyme == 'alternate rhyme' and metre == 'iambic tetrameter':
        return 'ballad stanza'

    if rhyme == 'couplets' and metre == 'iambic pentameter':
        return 'heroic couplets'

    if metre == 'iambic pentameter':
        return 'blank verse'

    return 'unknown form' 

if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        print(guess_form(f.read(), verbose=True))
