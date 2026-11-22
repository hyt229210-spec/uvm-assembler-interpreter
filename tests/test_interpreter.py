"""Tests for the virtual machine interpreter."""

import json
import tempfile
import unittest
from pathlib import Path

from src.virtual_machine import (
    VirtualMachine,
    VirtualMachineError,
    decode_program,
)


class TestVirtualMachine(unittest.TestCase):
    """Test instruction decoding and execution."""

    def test_decode_program(self):
        """Check decoding of machine instructions."""
        machine_code = bytes.fromhex(
            "06 E9 00 00 00 "
            "D0 1A "
            "05 25 01 00"
        )

        instructions = decode_program(machine_code)

        self.assertEqual(len(instructions), 3)
        self.assertEqual(instructions[0]["A"], 6)
        self.assertEqual(instructions[0]["B"], 466)
        self.assertEqual(instructions[1]["A"], 80)
        self.assertEqual(instructions[1]["B"], 53)
        self.assertEqual(instructions[2]["A"], 5)
        self.assertEqual(instructions[2]["B"], 586)

    def test_load_constant(self):
        """Check loading a constant into the accumulator."""
        instructions = [
            {"name": "load_const", "B": 466},
        ]

        machine = VirtualMachine(instructions)
        machine.execute()

        self.assertEqual(machine.accumulator, 466)

    def test_store_and_load(self):
        """Check writing and reading a memory value."""
        instructions = [
            {"name": "load_const", "B": 100},
            {"name": "load_const", "B": 42},
            {"name": "store", "B": 100},
            {"name": "load_const", "B": 100},
            {"name": "load", "B": 0},
        ]

        machine = VirtualMachine(instructions)
        machine.execute()

        self.assertEqual(machine.data_memory[100], 42)
        self.assertEqual(machine.accumulator, 42)

    def test_memory_copy(self):
        """Check copying values between memory regions."""
        instructions = [
            {"name": "load_const", "B": 10},
            {"name": "store", "B": 100},
            {"name": "load_const", "B": 20},
            {"name": "store", "B": 101},
            {"name": "load_const", "B": 30},
            {"name": "store", "B": 102},
            {"name": "load_const", "B": 100},
            {"name": "load", "B": 0},
            {"name": "store", "B": 200},
            {"name": "load_const", "B": 101},
            {"name": "load", "B": 0},
            {"name": "store", "B": 201},
            {"name": "load_const", "B": 102},
            {"name": "load", "B": 0},
            {"name": "store", "B": 202},
        ]

        machine = VirtualMachine(instructions)
        machine.execute()

        self.assertEqual(
            [machine.data_memory[i] for i in range(200, 203)],
            [10, 20, 30],
        )

    def test_save_json_dump(self):
        """Check saving memory to a JSON file."""
        instructions = [
            {"name": "load_const", "B": 42},
            {"name": "store", "B": 100},
        ]

        machine = VirtualMachine(instructions)
        machine.execute()

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "memory_dump.json"
            machine.save_memory_dump(path, 100, 101)

            with path.open("r", encoding="utf-8") as file:
                dump = json.load(file)

        self.assertEqual(dump["accumulator"], 42)
        self.assertEqual(
            dump["memory"][0],
            {"address": 100, "value": 42},
        )
        self.assertEqual(
            dump["memory"][1],
            {"address": 101, "value": 0},
        )

    def test_unknown_opcode(self):
        """Reject an unknown machine instruction."""
        with self.assertRaises(VirtualMachineError):
            decode_program(bytes([7]))

    def test_incomplete_instruction(self):
        """Reject an incomplete machine instruction."""
        with self.assertRaises(VirtualMachineError):
            decode_program(bytes([6, 0]))

    def test_out_of_range_address(self):
        """Reject a memory address outside the allowed range."""
        instructions = [
            {"name": "load_const", "B": 4194303},
            {"name": "load", "B": 1},
        ]

        machine = VirtualMachine(instructions)

        with self.assertRaises(VirtualMachineError):
            machine.execute()


if __name__ == "__main__":
    unittest.main()