"""Tests for the YAML assembler."""

import unittest

from src.assembler import (
    AssemblyError,
    translate_command,
    translate_program,
)


class TestAssembler(unittest.TestCase):
    """Test YAML command translation."""

    def test_all_commands(self):
        """Check translation of all four commands."""
        document = {
            "program": [
                {"command": "load_const", "value": 466},
                {"command": "load", "offset": 53},
                {"command": "store", "address": 586},
                {"command": "ror", "address": 683},
            ]
        }

        result = translate_program(document)

        self.assertEqual(len(result), 4)
        self.assertEqual(result[0]["A"], 6)
        self.assertEqual(result[0]["B"], 466)
        self.assertEqual(result[1]["A"], 80)
        self.assertEqual(result[1]["B"], 53)
        self.assertEqual(result[2]["A"], 5)
        self.assertEqual(result[2]["B"], 586)
        self.assertEqual(result[3]["A"], 123)
        self.assertEqual(result[3]["B"], 683)

    def test_unknown_command(self):
        """Reject unknown commands."""
        command = {"command": "unknown", "value": 10}

        with self.assertRaises(AssemblyError):
            translate_command(command, 1)

    def test_negative_value(self):
        """Reject negative operands."""
        command = {"command": "load_const", "value": -1}

        with self.assertRaises(AssemblyError):
            translate_command(command, 1)

    def test_value_out_of_range(self):
        """Reject operands exceeding the field size."""
        command = {"command": "load", "offset": 64}

        with self.assertRaises(AssemblyError):
            translate_command(command, 1)

    def test_missing_operand(self):
        """Reject commands without required operands."""
        command = {"command": "store"}

        with self.assertRaises(AssemblyError):
            translate_command(command, 1)

    def test_boolean_operand(self):
        """Reject boolean values as numeric operands."""
        command = {"command": "load_const", "value": True}

        with self.assertRaises(AssemblyError):
            translate_command(command, 1)

    def test_empty_program(self):
        """Reject empty programs."""
        document = {"program": []}

        with self.assertRaises(AssemblyError):
            translate_program(document)

    def test_invalid_document(self):
        """Reject documents without a program field."""
        document = {"commands": []}

        with self.assertRaises(AssemblyError):
            translate_program(document)


if __name__ == "__main__":
    unittest.main()