Poetry-Tools
===================
- Performs [prosodic](https://en.wikipedia.org/wiki/Prosody_%28linguistics%29) analysis of poetry. 
- Estimates rhyme scheme and metre using CMUDict, compares them against common forms using [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance), and combines the results to guess the form of the poem. 
- Contains a `rhymes` function that is faster than any other I have found.
- Contributions & pull requests welcome.

Requirements
------------
- Python >= 3.5
- python-Levenshtein >= 0.12.0

Examples
------------
Install with ```python setup.py install```

```python
>>> import poetrytools
>>> poetrytools.rhymes('show', 'hello')
True
>>> haiku = """savannah dust trails
... whistling thorn hovers above
... hungry giraffe grows"""
>>> poem = poetrytools.tokenize(haiku) # need to tokenize the poem first
>>> poetrytools.scanscion(poem)
[['010', '1', '1'], ['10', '1', '10', '01'], ['10', '01', '1']]
>>> poetrytools.guess_form(poem)
'haiku'
>>> limerick = """The limerick packs laughs anatomical
... Into space that is quite economical.
... But the good ones I've seen
... So seldom are clean
... And the clean ones so seldom are comical."""
>>> poem = poetrytools.tokenize(limerick)
>>> poetrytools.guess_form(poem, verbose=True)
Metre: 01001110100 00110110100 100111 11011 10111101100
Rhyme scheme: aabba

Closest metre: trochaic tetrameter
Closest rhyme: limerick
Guessed form: 'limerick'
```

Notes
------------

- For various reasons this library currently only works for short poems; the longer the poem is, the more inaccurate it gets.
- CMUDict is included as a JSON file in order to avoid importing the behemoth that is NLTK.

