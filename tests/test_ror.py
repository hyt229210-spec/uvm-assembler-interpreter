"""Tests for the rotate-right operation."""

import unittest

from src.virtual_machine import VirtualMachine


class TestRotateRight(unittest.TestCase):
    """Test 32-bit cyclic right rotation."""

    def run_rotation(self, value, shift):
        """Execute a rotation and return the result."""
        instructions = [
            {"name": "load_const", "B": shift},
            {"name": "store", "B": 10},
            {"name": "load_const", "B": value},
            {"name": "ror", "B": 10},
        ]

        machine = VirtualMachine(instructions)
        machine.execute()

        return machine.accumulator

    def test_rotate_right_by_eight(self):
        """Check rotation of a value by eight bits."""
        result = self.run_rotation(0x123456, 8)

        self.assertEqual(result, 0x56001234)

    def test_rotate_right_by_zero(self):
        """Check that zero shift preserves the value."""
        result = self.run_rotation(0x123456, 0)

        self.assertEqual(result, 0x00123456)

    def test_rotate_right_by_word_width(self):
        """Check that rotation by 32 bits preserves the value."""
        result = self.run_rotation(0x123456, 32)

        self.assertEqual(result, 0x00123456)

    def test_rotate_right_by_more_than_word_width(self):
        """Check that rotation count is reduced modulo 32."""
        result = self.run_rotation(0x123456, 40)

        self.assertEqual(result, 0x56001234)


if __name__ == "__main__":
    unittest.main()