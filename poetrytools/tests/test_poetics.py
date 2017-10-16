import os
import unittest
import poetrytools


class TestPoems(unittest.TestCase):
    def open_poem(self, poem):
        with open(os.path.join('poetrytools/poems', poem)) as f:
            return poetrytools.tokenize(f.read())

    def test_haiku(self):
        self.assertTrue(poetrytools.guess_form(
            self.open_poem('haiku.txt')) == 'haiku')
        self.assertTrue(poetrytools.guess_form(
            self.open_poem('tanka.txt')) == 'tanka')

    def test_sonnets(self):
        self.assertTrue(poetrytools.guess_form(
            self.open_poem('sonnet.txt')) == 'Shakespearean sonnet')
        self.assertTrue(poetrytools.guess_form(self.open_poem(
            'brokensonnet.txt')) == 'sonnet with unusual meter')

    def test_blankverse(self):
        self.assertTrue(poetrytools.guess_form(
            self.open_poem('blankverse.txt')) == 'blank verse')

    def test_cinquain(self):
        self.assertTrue(poetrytools.guess_form(
            self.open_poem('cinquain.txt')) == 'cinquain')

    def test_ottavarima(self):
        self.assertTrue(poetrytools.guess_form(
            self.open_poem('ottavarima.txt')) == 'ottava rima')

    def test_heroiccouplets(self):
        self.assertTrue(poetrytools.guess_form(
            self.open_poem('heroiccouplets.txt')) == 'heroic couplets')

    def test_rondeau(self):
        self.assertTrue(poetrytools.guess_form(
            self.open_poem('rondeau.txt')) == 'rondeau')


if __name__ == '__main__':
    unittest.main()
