Poetry-Tools
===================

Performs prosodic analysis of poetry. Determines rhyme scheme and metre using CMUDict, and guesses the form of the poem.

Requirements
------------
Python >= 2.7

nltk==3.0.1  
python-Levenshtein==0.12.0

NLTK Resources Required
-----------------------
corpora/cmudict  
tokenizers/punkt/english.pickle

ToDo
----
- Find a way to fuzz rhyme scheme matching (for instance, rhyme scheme analysis of sonnet.txt produces ['A', 'B', 'A', 'B', 'x', 'C', 'x', 'C', 'D', 'B', 'D', 'B', 'D', 'D'] because CMUDict is weird and doesn't think 'admire' and 'desire' are rhymes), but it needs to somehow match an ABABCDCDEFEFGG scheme so we can call it a Shakespearean sonnet. If it matched ABABCDCDEFGEFG then it would be an Italian/Petrarchan sonnet.
- Implement decision tree of poetic forms with help of Poetic_Forms.txt