"""Integration test for the final vector task."""

import unittest
from pathlib import Path

from src.assembler import read_yaml, translate_program
from src.encoder import encode_program
from src.virtual_machine import VirtualMachine, decode_program


class TestVectorProgram(unittest.TestCase):
    """Test rotation of two five-element vectors."""

    def test_five_element_vector_rotation(self):
        """Check all five results of the vector program."""
        root = Path(__file__).resolve().parents[1]
        source = root / "examples" / "vector_ror.yaml"

        document = read_yaml(source)
        program = translate_program(document)
        machine_code = encode_program(program)
        instructions = decode_program(machine_code)

        self.assertEqual(len(instructions), 40)
        self.assertEqual(len(machine_code), 165)

        machine = VirtualMachine(instructions)
        machine.execute()

        expected_source = [
            1193046,
            11259375,
            129,
            67108863,
            20281789,
        ]

        expected_results = [
            1442845236,
            4027235550,
            2147483712,
            4294902783,
            2046978803,
        ]

        source_values = [
            machine.data_memory[address]
            for address in range(100, 105)
        ]

        result_values = [
            machine.data_memory[address]
            for address in range(200, 205)
        ]

        self.assertEqual(source_values, expected_source)
        self.assertEqual(result_values, expected_results)


if __name__ == "__main__":
    unittest.main()