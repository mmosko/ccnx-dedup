import unittest

from ccndedup.hash_wrapper import fash_hash


class TestHashWrapper(unittest.TestCase):
    def test_eq(self):
        h1 = fash_hash(bytes(100 * [1]))
        h2 = fash_hash(bytes(100 * [1]))
        self.assertEqual(h1, h2)

    def test_neq(self):
        h1 = fash_hash(bytes(100 * [1]))
        h2 = fash_hash(bytes(100 * [2]))
        self.assertNotEqual(h1, h2)
