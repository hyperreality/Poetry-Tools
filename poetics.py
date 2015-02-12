#!/usr/bin/python

import sys, nltk, re, string
from curses.ascii import isdigit
from collections import defaultdict
from Levenshtein import distance
from countsyl import count_syllables

d = nltk.corpus.cmudict.dict()

notindic = [] # words not found in dic. Ultimately I want to collect a bunch of fancy vocabulary and submit it to the CMUDict for addition.

def poem_tokenizer(poem):
    lines = open(poem).readlines()
    tokens = []
    for l in lines:
        m = re.sub(r'[^0-9a-zA-Z\s\']', '', l) # cleans annoying punctuation, but keep apostrophes
        tokens.append([word for sent in nltk.sent_tokenize(m) for word in nltk.word_tokenize(sent)])
    return tokens

def stress_word(word): # todo: split words with dashes and send them back in individually
    if word in notindic or word not in d:
        guess = '10000000000'[:count_syllables(word)] # apply some rules to guess syllabic count; provisional logic for adding stress is to stress first syllable only
#       print("%s: guessed stress of %s" % (word, guess))
        return guess
    else: # cleans up the output from the CMUdict
        first = [' '.join([str(c) for c in lst]) for lst in max(d[word])]
        second = ''.join(first)
        third = ''.join([i for i in second if i.isdigit()]).replace('2', '1') # not interested in secondary stress
        return third   

def poem_stress_pattern(poem):
    p = poem_tokenizer(poem)
    stresses = []
    linecount = 0 

    for eachline in p:
        stresses.append([]) # add array dimension for each new line
        
        words = [w.lower() for w in eachline] # homogenize input
        exp = re.compile("[A-Za-z]+")

        for a in words:
                if exp.match(a): # if its valid word
                    stresses[linecount].append(stress_word(a))
        linecount += 1
    return stresses

def rhyme(w1, w2, level): # finds if two words rhyme

     # This catches words we don't know how to rhyme. Todo: Code a fallback function, for obvious rhymes like "cornucopia" and "utopia"
     if w1 in notindic or w2 in notindic: 
         return 0
     try:
         syllables = [' '.join([str(c) for c in lst]) for lst in d[w1.lower()]]
     except:
         notindic.append(w1)
         return 0
     try:
         syllables2 = [' '.join([str(c) for c in lst]) for lst in d[w2.lower()]]
     except:
         notindic.append(w2)
         return 0

     for syllable in syllables: # iterates through pronunciations of each word, tries to find one where LEVEL last syllables match
         for syllable2 in syllables2:
             if syllable2[-level:] == syllable[-level:]:
                 return 1
     return 0

def rhyme_scheme(poem):
    p = poem_tokenizer(poem)
    finalwords = [s[-1] for s in p if s]

    rhymescheme = ['x'] * len(finalwords)

    currline = 0
    currrhyme = 0
   
    rhymenotation = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'y', 'z']

    for i in string.ascii_uppercase:
        for j in string.ascii_lowercase:
            rhymenotation.append(i+j) # add 676 more ways of notating rhyme for long poems

    for word in finalwords:
        rhymed = False
        for i in range(currline+1,len(finalwords)):
            if rhymescheme[i] == 'x': # if word is not already part of a rhyme scheme
                if rhyme(word,finalwords[i],2):
                    rhymescheme[currline] = rhymenotation[currrhyme]
                    rhymescheme[i] = rhymenotation[currrhyme]
                    rhymed = True

        if rhymed == True: # if there was a rhyme, increment letter
            currrhyme += 1
        currline += 1

    # hunt for duplicate lines (in a sense, whole line rhymes)
    D = defaultdict(list)
    for i,item in enumerate(p):
        D[tuple(item)].append(i)
    duplicates = {k:v for k,v in D.items() if len(v)>1}  
    
    dupcount = 0
    for num in sorted(duplicates.values()):
        for n in num:
            rhymescheme[n] = rhymescheme[n] + str(dupcount) # add corresponding numbers to corresponding lines
        dupcount += 1

    return rhymescheme

def metrical_scheme(poem):
    p = poem_stress_pattern(poem)

    strip = [''.join(l) for l in p if l] # removes newlines here so length count is correct (alongside joining the inner lists)
    print(strip)
    linelengths = [len(l) for l in strip]
    numlines = len(strip)

    meters = {'iambic trimeter': '010101', 'iambic tetrameter': '01010101', 'iambic pentameter': '0101010101', 'trochaic tetrameter': '10101010', 'trochaic pentameter': '1010101010'}
    
    z = defaultdict(int) # a dict of summed Levenshtein distances
    for l in strip:
    	for v in meters.items():
            leven = distance(l,v[1])
            z[v[0]] += leven
    meter = min(z, key=z.get) # Minimum Levenshtein selected as best metrical match.
    print(z)
    return numlines, linelengths, meter

def find_form(poem):
    rhymes = rhyme_scheme(poem)
    print(rhymes)
    numlines, linelengths, meter = metrical_scheme(poem)

    if linelengths == [5,7,5]:
        return 'haiku'

    if numlines == 14:
        if meter == 'iambic pentameter':
            return 'Shakespearean sonnet'
        return 'sonnet with ' + meter + ' or irregular meter'

    return 'unknown'

if __name__ == '__main__':
    print("Form is " + find_form(sys.argv[1]))
    if notindic: 
        print("Unusual vocab that caused problems with stress and rhyme: " + ', '.join(set(notindic)))