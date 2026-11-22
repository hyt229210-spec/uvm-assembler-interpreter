"""Virtual machine with separate program and data memory."""

import json
from pathlib import Path


FIELD_A_BITS = 7
MEMORY_SIZE = 1 << 22

INSTRUCTION_SET = {
    6: {
        "name": "load_const",
        "size": 5,
        "operand_bits": 26,
    },
    80: {
        "name": "load",
        "size": 2,
        "operand_bits": 6,
    },
    5: {
        "name": "store",
        "size": 4,
        "operand_bits": 22,
    },
    123: {
        "name": "ror",
        "size": 4,
        "operand_bits": 22,
    },
}


class VirtualMachineError(Exception):
    """Error raised during virtual machine execution."""


def decode_program(machine_code):
    """Decode machine bytes into an instruction list."""
    if not machine_code:
        raise VirtualMachineError("Machine code is empty.")

    instructions = []
    position = 0

    while position < len(machine_code):
        opcode = machine_code[position] & 0x7F

        if opcode not in INSTRUCTION_SET:
            raise VirtualMachineError(
                f"Unknown opcode {opcode} at position {position}."
            )

        definition = INSTRUCTION_SET[opcode]
        size = definition["size"]
        end = position + size

        if end > len(machine_code):
            raise VirtualMachineError(
                f"Incomplete instruction at position {position}."
            )

        encoded = int.from_bytes(
            machine_code[position:end],
            byteorder="little",
        )
        operand = encoded >> FIELD_A_BITS
        maximum = (1 << definition["operand_bits"]) - 1

        if operand > maximum:
            raise VirtualMachineError(
                f"Invalid operand at position {position}."
            )

        instructions.append({
            "name": definition["name"],
            "A": opcode,
            "B": operand,
            "size": size,
        })

        position = end

    return instructions


class VirtualMachine:
    """Execute instructions using separate program and data memory."""

    def __init__(self, instructions):
        """Initialize program memory, data memory and accumulator."""
        self.program_memory = list(instructions)
        self.data_memory = {}
        self.accumulator = 0

    def check_address(self, address):
        """Check whether a data memory address is valid."""
        if address < 0 or address >= MEMORY_SIZE:
            raise VirtualMachineError(
                f"Memory address {address} is out of range."
            )

    def execute(self):
        """Execute all instructions in program memory."""
        for instruction in self.program_memory:
            name = instruction["name"]
            operand = instruction["B"]

            if name == "load_const":
                self.accumulator = operand

            elif name == "load":
                address = self.accumulator + operand
                self.check_address(address)
                self.accumulator = self.data_memory.get(
                    address,
                    0,
                )

            elif name == "store":
                self.check_address(operand)
                self.data_memory[operand] = self.accumulator

            elif name == "ror":
                raise VirtualMachineError(
                    "ROR operation will be implemented in stage 4."
                )

            else:
                raise VirtualMachineError(
                    f"Unsupported instruction: {name}."
                )

        return self.accumulator

    def save_memory_dump(self, path, start, end):
        """Save the selected memory range as a JSON file."""
        if start < 0 or end >= MEMORY_SIZE or start > end:
            raise VirtualMachineError(
                "Invalid memory dump address range."
            )

        memory = [
            {
                "address": address,
                "value": self.data_memory.get(address, 0),
            }
            for address in range(start, end + 1)
        ]

        dump = {
            "range": {
                "start": start,
                "end": end,
            },
            "accumulator": self.accumulator,
            "memory": memory,
        }

        output_path = Path(path)
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(dump, file, indent=4)