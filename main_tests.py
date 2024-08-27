import unittest
import main


class ColorFunctionsTest(unittest.TestCase):

    def test_parse_color(self):
        self.assertEqual(main.parse_color("000000"), [0, 0, 0])
        self.assertEqual(main.parse_color("0x000020"), [0, 0, 32])

        self.assertEqual(main.parse_color("640000"), [100, 0, 0])
        self.assertEqual(main.parse_color("0x640000"), [100, 0, 0])

