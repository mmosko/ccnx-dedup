#  Copyright 2024 Marc Mosko
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import unittest

from ccndedup.core.hash_wrapper import fash_hash


class TestHashWrapper(unittest.TestCase):
    def test_eq(self):
        h1 = fash_hash(bytes(100 * [1]))
        h2 = fash_hash(bytes(100 * [1]))
        self.assertEqual(h1, h2)

    def test_neq(self):
        h1 = fash_hash(bytes(100 * [1]))
        h2 = fash_hash(bytes(100 * [2]))
        self.assertNotEqual(h1, h2)
