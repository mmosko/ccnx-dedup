import unittest

from ccndedup.fastcdc.gear import gears


class TestGear(unittest.TestCase):
    def test_unique(self):
        s = list(gears)
        s.sort()
        for i in range(0, len(s)-1):
            self.assertNotEqual(s[i], s[i+1])
