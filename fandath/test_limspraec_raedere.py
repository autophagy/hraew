# -*- coding: utf-8 -*-
# This test suite tests the hraew rædere.

import unittest
from hraew import LimspræcRædere
import os

test_limspraec = """
[ testlim ]
nama    :: Test Lim
bleoh   :: bearht
beah    :: A testing lim.
hand    :: Hello world!
        ::
        :: This is a lim!
fingras :: source of this  :: https://github.com/autophagy/
        :: website         :: https://autophagy.io/

[ anotherlim ]
nama    :: Another Test Lim
bleoh   :: deorc
beah    :: Another testing lim.
""".strip()

expected_lim = {
    "testlim": {
        "nama": "Test Lim",
        "bleoh": "bearht",
        "beah": "A testing lim.",
        "hand": "Hello world!\n\nThis is a lim!",
        "fingras": {"source of this": "https://github.com/autophagy/",
                    "website": "https://autophagy.io/"}
    },
    "anotherlim": {
        "nama": "Another Test Lim",
        "bleoh": "deorc",
        "beah": "Another testing lim."
    },
}

PATH_TO_LIM = os.path.join(os.path.dirname(__file__), "test.lim")

class TestLimspræcRædere(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        f = open(PATH_TO_LIM, "w")
        f.write(test_limspraec)
        f.close()

    @classmethod
    def tearDownClass(cls):
        os.remove(PATH_TO_LIM)


    def test_block_identification(self):
        raedere = LimspræcRædere()
        read_lim = raedere.raed(PATH_TO_LIM)
        self.assertEqual(read_lim, expected_lim)
