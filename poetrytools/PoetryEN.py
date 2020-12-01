from Poetry import Poetry
from simpletokenizer import tokenize

class PoetryEN(Poetry):
    def __init__(self, path_to_dictionary):
        super(PoetryEN, self).__init__(path_to_dictionary)
        self.language = 'EN'

    def tokenize(self, poem : str):
        return tokenize(poem)

    def __language_specific_syllables__(self, syllables):
        # Work around some limitations of CMU
        equivalents = {"ER0": "R"}
        return [equivalents[syl] if syl in equivalents else syl for syl in syllables]
