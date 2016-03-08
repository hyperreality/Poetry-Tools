from unittest import TestCase

import os
import poetrytools

def open_poem(poem):
    with open(os.path.join('poetrytools/poems',poem)) as f:
        return f.read()

class TestPoems(TestCase):

    def test_haiku(self):
        self.assertTrue(poetrytools.guess_form(open_poem('haiku.txt')) == 'haiku')
        self.assertTrue(poetrytools.guess_form(open_poem('tanka.txt')) == 'tanka')

    def test_sonnets(self):
        self.assertTrue(poetrytools.guess_form(open_poem('sonnet.txt')) == 'Shakespearean sonnet')
        self.assertTrue(poetrytools.guess_form(open_poem('brokensonnet.txt')) == 'sonnet with trochaic pentameter or irregular meter')

    def test_blankverse(self):
        self.assertTrue(poetrytools.guess_form(open_poem('blankverse.txt')) == 'blank verse')

    def test_cinquain(self):
        self.assertTrue(poetrytools.guess_form(open_poem('cinquain.txt')) == 'cinquain')

if __name__ == '__main__':
    unittest.main()