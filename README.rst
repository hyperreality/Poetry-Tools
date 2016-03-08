Poetry-Tools
===================

- Performs prosodic analysis of poetry. 
- Estimates rhyme scheme and metre using CMUDict, and uses them to guess the form of the poem. 
- Contains a `rhymes` function that is faster than any other I have found.
- CMUDict is included as a JSON file in order to avoid importing NLTK.

Requirements
------------
- Python >= 2.7
- python-Levenshtein==0.12.0