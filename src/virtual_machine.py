"""Virtual machine with separate program and data memory."""

import json
from pathlib import Path


FIELD_A_BITS = 7
MIN_ADDRESS = 0
MEMORY_SIZE = 1 << 22
WORD_BITS = 32
WORD_MASK = (1 << WORD_BITS) - 1

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


def decode_instruction(machine_code, position):
    """Decode one instruction at the given byte position."""
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

    instruction = {
        "name": definition["name"],
        "A": opcode,
        "B": operand,
        "size": size,
    }

    return instruction, end


def decode_program(machine_code):
    """Decode all machine bytes into an instruction list."""
    if not machine_code:
        raise VirtualMachineError("Machine code is empty.")

    instructions = []
    position = 0

    while position < len(machine_code):
        instruction, position = decode_instruction(
            machine_code,
            position,
        )
        instructions.append(instruction)

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
        if address < MIN_ADDRESS or address >= MEMORY_SIZE:
            raise VirtualMachineError(
                f"Memory address {address} is out of range."
            )

    def _load_value(self, offset):
        """Load a value from data memory."""
        address = self.accumulator + offset
        self.check_address(address)
        self.accumulator = self.data_memory.get(address, 0)

    def _store_value(self, address):
        """Store the accumulator in data memory."""
        self.check_address(address)
        self.data_memory[address] = self.accumulator

    def _rotate_right(self, address):
        """Rotate the accumulator to the right."""
        self.check_address(address)
        shift = self.data_memory.get(address, 0) % WORD_BITS
        value = self.accumulator & WORD_MASK

        self.accumulator = (
            (value >> shift)
            | (value << (WORD_BITS - shift))
        ) & WORD_MASK

    def _execute_instruction(self, instruction):
        """Execute one decoded instruction."""
        name = instruction["name"]
        operand = instruction["B"]

        if name == "load_const":
            self.accumulator = operand
        elif name == "load":
            self._load_value(operand)
        elif name == "store":
            self._store_value(operand)
        elif name == "ror":
            self._rotate_right(operand)
        else:
            raise VirtualMachineError(
                f"Unsupported instruction: {name}."
            )

    def execute(self):
        """Execute all instructions in program memory."""
        for instruction in self.program_memory:
            self._execute_instruction(instruction)

        return self.accumulator

    def save_memory_dump(self, path, start, end):
        """Save the selected memory range as a JSON file."""
        if (
            start < MIN_ADDRESS
            or end >= MEMORY_SIZE
            or start > end
        ):
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
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(dump, file, indent=4)