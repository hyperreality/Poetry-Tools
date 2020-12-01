import os
import unittest
from poetrytools import PoetryEN


class TestENPoems(unittest.TestCase):
    def setUp(self):
        self.poetryEN = PoetryEN('cmudict/cmudict.json')
        t = os.getcwd()
        print(os.curdir)


    def open_poem(self, poem):
        with open(os.path.join('..','poems', poem)) as f:
            return self.poetryEN.tokenize(f.read())

    def test_haiku(self):
        self.assertTrue(self.poetryEN.guess_form(
            self.open_poem('haiku.txt')) == 'haiku')
        self.assertTrue(self.poetryEN.guess_form(
            self.open_poem('tanka.txt')) == 'tanka')

    def test_sonnets(self):
        print(os.curdir)
        self.assertTrue(self.poetryEN.guess_form(
            self.open_poem('sonnet.txt')) == 'Shakespearean sonnet')
        self.assertTrue(self.poetryEN.guess_form(self.open_poem(
            'brokensonnet.txt')) == 'sonnet with unusual meter')

    def test_blankverse(self):
        self.assertTrue(self.poetryEN.guess_form(
            self.open_poem('blankverse.txt')) == 'blank verse')

    def test_cinquain(self):
        self.assertTrue(self.poetryEN.guess_form(
            self.open_poem('cinquain.txt')) == 'cinquain')

    def test_ottavarima(self):
        self.assertTrue(self.poetryEN.guess_form(
            self.open_poem('ottavarima.txt')) == 'ottava rima')

    def test_heroiccouplets(self):
        self.assertTrue(self.poetryEN.guess_form(
            self.open_poem('heroiccouplets.txt')) == 'heroic couplets')

    def test_rondeau(self):
        self.assertTrue(self.poetryEN.guess_form(
            self.open_poem('rondeau.txt')) == 'rondeau')


if __name__ == '__main__':
    unittest.main()
