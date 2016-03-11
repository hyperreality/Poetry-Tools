Poetry-Tools
===================

- Performs prosodic analysis of poetry. 
- Estimates rhyme scheme and metre using CMUDict, and uses them to guess the form of the poem. 
- Contains a `rhymes` function that is faster than any other I have found.

Notes / ToDo
------------
- At the moment there is a problem with different rhyme schemes overlapping, i.e. some alternate rhyme poems (ABAB CDCD) are being tagged as terza rima poems (ABA BCB CDC DED) and vice-versa.
- Detecting stanza length (tercets, quatrains) is not yet part of the logic.
- Many more poetic forms can be added once the above are implemented.
- Contributions & pull requests welcome.

Requirements
------------
- Python >= 2.7 or Python 3
- python-Levenshtein==0.12.0

(CMUDict is included as a JSON file in order to avoid importing the behemoth that is NLTK)
