#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Simple tokenizer. Remove or replace unwanted characters, and parse to a list of lists of sentences and words
"""

import re, unicodedata

def remove_accents(string):
    """
    Removes unicode accents from a string, downgrading to the base character
    """

    nfkd = unicodedata.normalize('NFKD', string)
    return u"".join([c for c in nfkd if not unicodedata.combining(c)])

def tokenize(poem):

    tokens = []

    # Problematic characters to replace before regex
    replacements = {u'-': u' ', u'—': u' ', u'\'d': u'ed'}

    for original, replacement in replacements.items():
        replaced = poem.replace(original, replacement)
    replaced = remove_accents(replaced)

    # Keep apostrophes, discard other non-alphanumeric symbols
    cleaned = re.sub(r'[^0-9a-zA-Z\s\']', '', replaced)

    for line in cleaned.split('\n'):
        tokens.append([word for word in line.strip().split(' ')])

    return tokens
