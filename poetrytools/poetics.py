#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import print_function
import sys
import codecs

from PoetryEN import PoetryEN

if __name__ == '__main__':
    poetryEN = PoetryEN('cmudict/cmudict.json')
    if len(sys.argv) == 2:
        with codecs.open(sys.argv[1], 'r', 'utf-8') as f:
            poem = f.read()
        tokenized = poetryEN.tokenize(poem)
        print(poetryEN.guess_form(tokenized, verbose=True))
    else:
        print("Please provide a poem to analyse, i.e.: poetics.py poems/sonnet.txt")
