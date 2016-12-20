#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import print_function
import json, os, re, sys, codecs, unicodedata
from collections import defaultdict
from string import ascii_lowercase
from Levenshtein import distance
from .countsyl import count_syllables

# Import CMU dictionary
with open(os.path.join(os.path.dirname(__file__), 'cmudict/cmudict.json')) as json_file:
    cmu = json.load(json_file)

possible_metres = {
    'iambic trimeter'     : '010101',
    'iambic tetrameter'   : '01010101',
    'iambic pentameter'   : '0101010101',
    'trochaic tetrameter' : '10101010',
    'trochaic pentameter' : '1010101010'
}

possible_rhymes = {
    'couplets'            : 'aabbccddeeff',
    'alternate rhyme'     : 'ababcdcdefefghgh',
    'enclosed rhyme'      : 'abbacddceffe',
    'rima'                : 'ababcbcdcdedefefgfghg',
    'rondeau rhyme'       : 'aabbaaabCaabbaC',
    'shakespearean sonnet': 'ababcdcdefefgg',
    'limerick'            : 'aabba',
    'no rhyme'            : 'XXXX'
}

possible_stanzas = {
    'sonnet'              : '14,',
    'tercets'             : '3,'
}

def remove_accents(string):
    """
    Removes unicode accents from a string, downgrading to the base character
    """

    nfkd = unicodedata.normalize('NFKD', string)
    return u"".join([c for c in nfkd if not unicodedata.combining(c)])

def tokenize(poem):
    """
    Simple tokenizer. Remove or replace unwanted characters, then parse to a list of lists of sentences and words
    """

    tokens = []

    # Problematic characters to replace
    replacements = {u'-': u' ', u'—': u' ', u'\'d': u'ed'}

    for original, replacement in replacements.items():
        replaced = poem.replace(original, replacement)
    replaced = remove_accents(replaced)
    # Keep apostrophes, discard everything else
    cleaned = re.sub(r'[^0-9a-zA-Z\s\']', '', replaced)

    for line in cleaned.split('\n'):
        tokens.append([word for word in line.strip().split(' ')])
    return tokens

def getSyllables(word):
    """
    Look up a word in the CMU dictionary, return a list of syllables
    """

    try:
        return(cmu[word.lower()])
    except KeyError:
        return False

def stress(word):
    """
    Represent strong and weak stress of a word with a series of 1's and 0's
    """

    syllables = getSyllables(word)

    if syllables:
        # TODO: Implement a more advanced way of handling multiple pronunciations than just using the min
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

    # By default, nothing rhymes
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

def get_lowest(dictionary):
    """
    Get the lowest value of a dictionary, returning its key
    """

    return min(dictionary, key = dictionary.get)

def levenshtein(string, candidates):
    """
    Compare a string's Levenshtein distance to each candidate in a dictionary. Expands the length of each candidate to match the length of the compared string
    Returns the name of the closest match
    """

    distances = defaultdict(int)
    num_lines = len(string)

    for k, v in candidates.items():
        expanded = (v * (num_lines // len(v) + 1))[:num_lines]
        distances[k] += distance(string, expanded)

    return get_lowest(distances)

def guess_metre(poem):
    """
    Guess a poem's metre via Levenshtein distance from candidates
    """

    joined_lines = [''.join(line) for line in scanscion(poem) if line]
    line_lengths = [len(line) for line in joined_lines]
    num_lines    = len(joined_lines)

    z = defaultdict(int)
    for line in joined_lines:
        for metre, notation in possible_metres.items():
            z[metre] += distance(line, notation)

    guessed_metre = get_lowest(z)

    return joined_lines, num_lines, line_lengths, guessed_metre

def guess_rhyme_type(poem):
    """
    Guess a poem's rhyme via Levenshtein distance from candidates
    """

    joined_lines = ''.join([l for l in rhyme_scheme(poem) if l])
    no_blanks = joined_lines.replace(' ', '')

    guessed_rhyme = levenshtein(no_blanks, possible_rhymes)
    return joined_lines, guessed_rhyme

def stanza_lengths(poem):
    """
    Returns a comma-delimited string of stanza lengths
    """

    stanzas = []

    i = 0
    for line in poem:
        if line != ['']:
            i += 1
        else:
            stanzas.append(str(i))
            i = 0
    if i != 0:
        stanzas.append(str(i))

    joined = ','.join(stanzas)

    guessed_stanza = levenshtein(joined, possible_stanzas)
    return joined, guessed_stanza

def guess_form(poem, verbose=False):
    def within_ranges(line_properties, ranges):
        if all([ranges[i][0] <= line_properties[i] <= ranges[i][1] for i in range(len(ranges))]):
            return True

    poem = tokenize(poem)

    metrical_scheme, num_lines, line_lengths, metre = guess_metre(poem)
    rhyme_scheme_string, rhyme = guess_rhyme_type(poem)
    stanza_length_string, stanza = stanza_lengths(poem)

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
    with codecs.open(sys.argv[1], 'r', 'utf-8') as f:
        print(guess_form(f.read(), verbose=True))

