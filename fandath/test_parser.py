# -*- coding: utf-8 -*-
import unittest
from hraew import Geþeodan, Biliþ, Cunnungarc, Gewissung, Paragraph


class TestParagraphParse(unittest.TestCase):

    paragraph_definition = (
        "hello [GEÞEODAN :: https://hraew.autophagy.io :: Test] world"
    )
    expected_geþeodan = {"uri": "https://hraew.autophagy.io", "text": "Test"}

    def test_paragraph(self):
        p = Paragraph("lim", self.paragraph_definition)
        p.parse()
        paragraph_options = p.template_options["paragraph"]
        self.assertTrue(isinstance(paragraph_options[0], str))
        self.assertTrue(isinstance(paragraph_options[1], Geþeodan))
        self.assertTrue(isinstance(paragraph_options[2], str))
        self.assertEqual(paragraph_options[1].template_options, self.expected_geþeodan)


class TestGeþeodanParser(unittest.TestCase):

    def test_geþeodan_with_text(self):
        geþeodan_definition = "[GEÞEODAN :: https://hraew.autophagy.io :: Test]"

        expected_options = {"uri": "https://hraew.autophagy.io", "text": "Test"}

        g = Geþeodan("lim", geþeodan_definition)
        g.parse()
        self.assertEqual(g.template_options, expected_options)

    def test_geþeodan_without_text(self):
        geþeodan_definition = "[GEÞEODAN :: https://hraew.autophagy.io]"

        expected_options = {
            "uri": "https://hraew.autophagy.io",
            "text": "https://hraew.autophagy.io",
        }

        g = Geþeodan("lim", geþeodan_definition)
        g.parse()
        self.assertEqual(g.template_options, expected_options)


class TestBiliþParser(unittest.TestCase):

    biliþ_definition = (
        """
    [BILIÞ]
    [test.png :: a test image]
    """.strip()
    )

    expected_options = {
        "lim_key": "lim",
        "image_uri": "test.png",
        "image_alt": "a test image",
    }

    def test_biliþ(self):
        b = Biliþ("lim", self.biliþ_definition)
        b.parse()
        self.assertEqual(b.template_options, self.expected_options)


class TestCunnungarcParser(unittest.TestCase):

    cunnungarc_definition = (
        """
    [CUNNUNGARC]
    [ SEASON        | FRENCH         | OLD ENGLISH | TRANSLATION                 ]
    [ Autumn        | Vendémiaire    | Hærfest     | Harvest, autumn             ]
    [               | Brumaire       | Mist        | Mist, fog                   ]
    [               | Frimaire       | Forst       | Frost                       ]
    [ Winter        | Nivôse         | Snáw        | Snow                        ]
    [               | Pluviôse       | Reg         | Rain                        ]
    [               | Ventôse        | Wind        | Wind                        ]
    [ Spring        | Germinal       | Sǽd        | Seed                        ]
    [               | Floréal        | Blóstm      | Blossom, flower             ]
    [               | Prairial       | Mǽdland    | Meadow-land                 ]
    [ Summer        | Messidor       | Ríp         | Reaping, harvest            ]
    [               | Thermidor      | Hát         | Heat                        ]
    [               | Fructidor      | Wæstm       | Growth, produce, fruit      ]
    [ Complementary | Sansculottides | Wending     | A turning round, revolution ]
    """.strip()
    )

    expected_headers = ["SEASON", "FRENCH", "OLD ENGLISH", "TRANSLATION"]
    expected_rows = [
        ["Autumn", "Vendémiaire", "Hærfest", "Harvest, autumn"],
        ["", "Brumaire", "Mist", "Mist, fog"],
        ["", "Frimaire", "Forst", "Frost"],
        ["Winter", "Nivôse", "Snáw", "Snow"],
        ["", "Pluviôse", "Reg", "Rain"],
        ["", "Ventôse", "Wind", "Wind"],
        ["Spring", "Germinal", "Sǽd", "Seed"],
        ["", "Floréal", "Blóstm", "Blossom, flower"],
        ["", "Prairial", "Mǽdland", "Meadow-land"],
        ["Summer", "Messidor", "Ríp", "Reaping, harvest"],
        ["", "Thermidor", "Hát", "Heat"],
        ["", "Fructidor", "Wæstm", "Growth, produce, fruit"],
        ["Complementary", "Sansculottides", "Wending", "A turning round, revolution"],
    ]

    def test_cunnungarc(self):
        c = Cunnungarc("lim", self.cunnungarc_definition)
        c.parse()
        self.assertEqual(c.template_options["headers"], self.expected_headers)
        self.assertEqual(c.template_options["rows"], self.expected_rows)


class TestGewissungParser(unittest.TestCase):

    gewissung_internal = (
        """
// INVOKER :: Wísdómhord
// DESCRIPTION :: An example hord
// INCEPT :: 10 Regn 226 // 05.00
// UPDATED :: 10 Regn 226 // 05.40
// COUNT :: 7

Hello world!

[ COL1          | COL2  | COL3  | COL4        ]
[ Hello world   | 12345 | True  | Wé          ]
[ Wes Hál       | 67890 | False | Gárdena     ]
[ Hallo Welt    | 123   | True  | in          ]
[ Saluton mondo | 34.2  | False | géardagum   ]
[ qo' vIvan     | 42    | True  | þéodcyninga ]
[ Suilad ambar  | 1968  |       | þrym        ]
[ Ada mūnok     |       | True  | gefrúnon    ]
""".strip()
    )

    gewissung_definition = """
[GEWISSUNG]
{}
[GEWISSUNGENDE]
""".strip().format(
        gewissung_internal
    )

    def test_gewissung(self):
        elements = self.gewissung_definition.split("\n\n")
        g = Gewissung("lim", elements[0])

        for e in elements[1:]:
            g.add_element(e)

        g.parse()
        parsed_block = "\n\n".join(g.template_options["elements"])
        self.assertEqual(parsed_block, self.gewissung_internal)
