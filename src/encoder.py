"""Machine code encoder for the educational virtual machine."""

FIELD_A_BITS = 7


def encode_instruction(instruction):
    """Convert one intermediate instruction into machine bytes."""
    opcode = instruction["A"]
    operand = instruction["B"]
    size = instruction["size"]

    combined = opcode | (operand << FIELD_A_BITS)

    return combined.to_bytes(size, byteorder="little")


def encode_program(program):
    """Convert a complete program into machine code."""
    return b"".join(
        encode_instruction(instruction)
        for instruction in program
    )