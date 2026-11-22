"""Command-line interpreter for the virtual machine."""

import argparse
import sys
from pathlib import Path

try:
    from .virtual_machine import (
        VirtualMachine,
        VirtualMachineError,
        decode_program,
    )
except ImportError:
    from virtual_machine import (
        VirtualMachine,
        VirtualMachineError,
        decode_program,
    )


def create_argument_parser():
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Educational virtual machine interpreter."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to machine code file",
    )
    parser.add_argument(
        "dump",
        type=Path,
        help="Path to JSON memory dump",
    )
    parser.add_argument(
        "start",
        type=int,
        help="First memory address to display",
    )
    parser.add_argument(
        "end",
        type=int,
        help="Last memory address to display",
    )
    return parser


def execute_program(args):
    """Load and execute a binary program."""
    machine_code = args.input.read_bytes()
    instructions = decode_program(machine_code)

    machine = VirtualMachine(instructions)
    machine.execute()

    machine.save_memory_dump(
        args.dump,
        args.start,
        args.end,
    )

    return instructions, machine


def main():
    """Run the virtual machine interpreter."""
    parser = create_argument_parser()
    args = parser.parse_args()

    try:
        instructions, machine = execute_program(args)
    except (OSError, VirtualMachineError) as error:
        print(f"Interpreter error: {error}", file=sys.stderr)
        return 1

    print(f"Executed commands: {len(instructions)}")
    print(f"Accumulator: {machine.accumulator}")
    print(f"Memory dump: {args.dump}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())