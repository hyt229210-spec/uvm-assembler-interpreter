"""Tests for machine code encoding."""

import unittest

from src.encoder import encode_instruction, encode_program


class TestEncoder(unittest.TestCase):
    """Test machine code generation."""

    def test_load_const_encoding(self):
        instruction = {
            "A": 6,
            "B": 466,
            "size": 5,
        }

        self.assertEqual(
            encode_instruction(instruction),
            bytes.fromhex("06 E9 00 00 00"),
        )

    def test_load_encoding(self):
        instruction = {
            "A": 80,
            "B": 53,
            "size": 2,
        }

        self.assertEqual(
            encode_instruction(instruction),
            bytes.fromhex("D0 1A"),
        )

    def test_store_encoding(self):
        instruction = {
            "A": 5,
            "B": 586,
            "size": 4,
        }

        self.assertEqual(
            encode_instruction(instruction),
            bytes.fromhex("05 25 01 00"),
        )

    def test_ror_encoding(self):
        instruction = {
            "A": 123,
            "B": 683,
            "size": 4,
        }

        self.assertEqual(
            encode_instruction(instruction),
            bytes.fromhex("FB 55 01 00"),
        )

    def test_complete_program(self):
        program = [
            {"A": 6, "B": 466, "size": 5},
            {"A": 80, "B": 53, "size": 2},
            {"A": 5, "B": 586, "size": 4},
            {"A": 123, "B": 683, "size": 4},
        ]

        expected = bytes.fromhex(
            "06 E9 00 00 00 "
            "D0 1A "
            "05 25 01 00 "
            "FB 55 01 00"
        )

        self.assertEqual(encode_program(program), expected)
        self.assertEqual(len(encode_program(program)), 15)


if __name__ == "__main__":
    unittest.main()