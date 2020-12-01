import json
import os
import sys
import codecs
from collections import defaultdict
from string import ascii_lowercase
from Levenshtein import distance
from countsyl import count_syllables
from simpletokenizer import tokenize

POSSIBLE_METRES = {
    'iambic trimeter': '010101',
    'iambic tetrameter': '01010101',
    'iambic pentameter': '0101010101',
    'trochaic tetrameter': '10101010',
    'trochaic pentameter': '1010101010'
}

POSSIBLE_RHYMES = {
    'couplets': 'aabbccddeeff',
    'alternate rhyme': 'ababcdcdefefghgh',
    'enclosed rhyme': 'abbacddceffe',
    'rima': 'ababcbcdcdedefefgfghg',
    'rondeau rhyme': 'aabbaaabCaabbaC',
    'shakespearean sonnet': 'ababcdcdefefgg',
    'limerick': 'aabba',
    'no rhyme': 'XXXX'
}

POSSIBLE_STANZAS = {
    'sonnet': '14,',
    'cinquains': '5,',
    'quatrains': '4,',
    'tercets': '3,'
}

class Poetry:
    def __init__(self, path_to_CMU):
        self.CMU = None
        self.__load__CMU__file(path_to_CMU)

    # def tokenize(self, poem : str):
    #     pass

    def __load__CMU__file(self, path_to_CMU : str):
        # Load up the CMU dictionary
        with open(os.path.join(os.path.dirname(__file__), path_to_CMU)) as json_file:
            self.CMU = json.load(json_file)

    @staticmethod
    def num_vowels(syllables):
        return len([syl for syl in syllables if any(char.isdigit() for char in syl)])

    def get_syllables(self, word):
        """
        Look up a word in the CMU dictionary, return a list of syllables
        """
        try:
            return self.CMU[word.lower()]
        except KeyError:
            return False

    def stress(self, word):
        """
        Represent strong and weak stress of a word with a series of 1's and 0's
        """

        syllables = self.get_syllables(word)

        if syllables:
            # TODO: Implement a more advanced way of handling multiple pronunciations than just picking the first
            pronunciation_string = ''.join(syllables[0])
            # Not interested in secondary stress
            stress_numbers = ''.join([x.replace('2', '1')
                                      for x in pronunciation_string if x.isdigit()])

            return stress_numbers

        # Provisional logic for adding stress when the word is not in the dictionary is to stress first syllable only
        return '1' + '0' * (count_syllables(word) - 1)

    def scanscion(self, tokenized_poem):
        """
        Get stress notation for every line in the poem
        """

        line_stresses = []
        currline = 0

        for line in tokenized_poem:
            line_stresses.append([])
            [line_stresses[currline].append(self.stress(word)) for word in line if word]
            currline += 1

        return line_stresses

    def replace_syllables(self, syllables):
        return self.__language_specific_syllables__(syllables)

    def __language_specific_syllables__(self, syllables):
        # Work around some limitations of CMU
        # equivalents = {"ER0": "R"}
        # def replace_syllables(syllables):
        #     return [equivalents[syl] if syl in equivalents else syl for syl in syllables]
        pass

    def rhymes(self, word1, word2, level=2):
        """
        For each word, get a list of various syllabic pronunications. Then check whether the last level number of syllables is pronounced the same. If so, the words probably rhyme
        """

        pronunciations = self.get_syllables(word1)
        pronunciations2 = self.get_syllables(word2)

        if not (pronunciations and pronunciations2):
            return False

        for syllables in pronunciations:
            syllables = self.replace_syllables(syllables)
            syls = level # Default number of syllables to check back from
            # If word only has a single vowel (i.e. 'stew'), then we reduce this to 1 otherwise we won't find a monosyllabic rhyme
            if Poetry.num_vowels(syllables) == 1:
                syls = 1

            for syllables2 in pronunciations2:
                syllables2 = self.replace_syllables(syllables2)
                if syllables[-syls:] == syllables2[-syls:]:
                    return True

        return False

    @staticmethod
    def stanza_lengths(tokenized_poem):
        """
        Returns a comma-delimited string of stanza lengths
        """

        stanzas = []

        i = 0
        for line in tokenized_poem:
            if line != ['']:
                i += 1
            else:
                stanzas.append(str(i))
                i = 0
        if i != 0:
            stanzas.append(str(i))

        joined = ','.join(stanzas)
        return joined

    def rhyme_scheme(self, tokenized_poem):
        """
        Get a rhyme scheme for the poem. For each line, lookahead to the future lines of the poem and see whether last words rhyme.
        """

        num_lines = len(tokenized_poem)

        # By default, nothing rhymes
        scheme = ['X'] * num_lines

        rhyme_notation = list(ascii_lowercase)
        currrhyme = -1  # Index into the rhyme_notation

        for lineno in range(0, num_lines):
            matched = False
            for futurelineno in range(lineno + 1, num_lines):
                # If next line is not already part of a rhyme scheme
                if scheme[futurelineno] == 'X':
                    base_line = tokenized_poem[lineno]
                    current_line = tokenized_poem[futurelineno]

                    if base_line == ['']:  # If blank line, represent that in the notation
                        scheme[lineno] = ' '

                    elif self.rhymes(base_line[-1], current_line[-1]):
                        if not matched:  # Increment the rhyme notation
                            matched = True
                            currrhyme += 1

                        if base_line == current_line:  # Capitalise rhyme if the whole line is identical
                            scheme[lineno] = scheme[futurelineno] = rhyme_notation[currrhyme].upper()
                        else:
                            scheme[lineno] = scheme[futurelineno] = rhyme_notation[currrhyme]

        return scheme

    @staticmethod
    def guess_stanza_type(tokenized_poem):
        joined_lengths = Poetry.stanza_lengths(tokenized_poem)

        guessed_stanza = Poetry.levenshtein(joined_lengths, POSSIBLE_STANZAS)
        return joined_lengths, guessed_stanza

    @staticmethod
    def levenshtein(string, candidates):
        """
        Compare a string's Levenshtein distance to each candidate in a dictionary.
        Returns the name of the closest match
        """

        distances = defaultdict(int)
        num_lines = len(string)

        for k, v in candidates.items():
            expanded = False
            # Expands the length of each candidate to match the length of the compared string
            if len(v) != len(string):
                v = (v * (num_lines // len(v) + 1))[:num_lines]
                expanded = True

            edit_distance = distance(string, v)

            # If we expanded the candidate, then it is a worse match than what we have already
            if edit_distance in distances and expanded:
                continue

            distances[distance(string, v)] = k

        return distances[min(distances)]

    def guess_rhyme_type(self, tokenized_poem):
        """
        Guess a poem's rhyme via Levenshtein distance from candidates
        """

        joined_lines = ''.join(self.rhyme_scheme(tokenized_poem))
        no_blanks = joined_lines.replace(' ', '')

        guessed_rhyme = Poetry.levenshtein(no_blanks, POSSIBLE_RHYMES)
        return joined_lines, guessed_rhyme

    def guess_metre(self, tokenized_poem):
        """
        Guess a poem's metre via Levenshtein distance from candidates
        """

        joined_lines = [''.join(line) for line in self.scanscion(tokenized_poem) if line]
        line_lengths = [len(line) for line in joined_lines]
        num_lines = len(joined_lines)

        metres = []
        for line in joined_lines:
            metres.append(Poetry.levenshtein(line, POSSIBLE_METRES))

        guessed_metre = max(zip((metres.count(item) for item in set(metres)), set(metres)))[1]

        return joined_lines, num_lines, line_lengths, guessed_metre

    def guess_form(self, tokenized_poem, verbose=False):
        def within_ranges(line_properties, ranges):
            if all([ranges[i][0] <= line_properties[i] <= ranges[i][1] for i in range(len(ranges))]):
                return True

        metrical_scheme, num_lines, line_lengths, metre = self.guess_metre(tokenized_poem)
        rhyme_scheme_string, rhyme = self.guess_rhyme_type(tokenized_poem)
        stanza_length_string, stanza = Poetry.guess_stanza_type(tokenized_poem)

        if verbose:
            print("Metre: " + ' '.join(metrical_scheme))
            print("Rhyme scheme: " + rhyme_scheme_string)
            print("Stanza lengths: " + stanza_length_string)
            print()
            print("Closest metre: " + metre)
            print("Closest rhyme: " + rhyme)
            print("Closest stanza type: " + stanza)
            print("Guessed form: ", end="")

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
            return 'sonnet with unusual meter'

        if num_lines == 15:
            return 'rondeau'

        if rhyme == 'alternate rhyme' and metre == 'iambic tetrameter':
            return 'ballad stanza'

        if metre == 'iambic pentameter':
            if rhyme == 'couplets' or rhyme == 'shakespearean sonnet':
                return 'heroic couplets'
            if rhyme == 'alternate rhyme':
                return 'Sicilian quatrain'
            return 'blank verse'

        return 'unknown form'