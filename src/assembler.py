"""YAML assembler for the educational virtual machine."""

import argparse
import sys
from pathlib import Path

import yaml


COMMANDS = {
    "load_const": {
        "opcode": 6,
        "operand": "value",
        "bits": 26,
        "size": 5,
    },
    "load": {
        "opcode": 80,
        "operand": "offset",
        "bits": 6,
        "size": 2,
    },
    "store": {
        "opcode": 5,
        "operand": "address",
        "bits": 22,
        "size": 4,
    },
    "ror": {
        "opcode": 123,
        "operand": "address",
        "bits": 22,
        "size": 4,
    },
}


class AssemblyError(Exception):
    """Error raised when an assembly program is invalid."""


def read_yaml(path: Path):
    """Read a YAML file and return its contents."""
    try:
        with path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except OSError as error:
        raise AssemblyError(
            f"Cannot read file: {path}"
        ) from error
    except yaml.YAMLError as error:
        raise AssemblyError(
            f"Invalid YAML format: {error}"
        ) from error


def translate_command(command, index):
    """Translate one YAML command into an intermediate form."""
    if not isinstance(command, dict):
        raise AssemblyError(
            f"Command {index}: expected a YAML object."
        )

    name = command.get("command")

    if name not in COMMANDS:
        raise AssemblyError(
            f"Command {index}: unknown command '{name}'."
        )

    definition = COMMANDS[name]
    operand_name = definition["operand"]
    expected_fields = {"command", operand_name}

    if set(command) != expected_fields:
        raise AssemblyError(
            f"Command {index}: expected fields "
            f"{expected_fields}."
        )

    value = command[operand_name]

    if isinstance(value, bool) or not isinstance(value, int):
        raise AssemblyError(
            f"Command {index}: operand must be an integer."
        )

    maximum = (1 << definition["bits"]) - 1

    if value < 0 or value > maximum:
        raise AssemblyError(
            f"Command {index}: value must be from 0 to {maximum}."
        )

    return {
        "name": name,
        "A": definition["opcode"],
        "B": value,
        "size": definition["size"],
    }


def translate_program(document):
    """Translate a complete YAML document into an instruction list."""
    if not isinstance(document, dict) or set(document) != {"program"}:
        raise AssemblyError(
            "The YAML document must contain only the 'program' field."
        )

    commands = document["program"]

    if not isinstance(commands, list) or not commands:
        raise AssemblyError(
            "The 'program' field must contain a non-empty list."
        )

    return [
        translate_command(command, index)
        for index, command in enumerate(commands, start=1)
    ]


def print_representation(program):
    """Print the intermediate representation."""
    print("\nIntermediate representation:")

    for index, instruction in enumerate(program, start=1):
        print(
            f"{index}. {instruction['name']}: "
            f"A={instruction['A']}, B={instruction['B']}, "
            f"size={instruction['size']} bytes"
        )


def main():
    """Run the assembler command-line application."""
    parser = argparse.ArgumentParser(
        description="Assembler for educational virtual machine."
    )
    parser.add_argument("input", type=Path, help="Input YAML file")
    parser.add_argument("output", type=Path, help="Output binary file")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Print intermediate representation",
    )

    args = parser.parse_args()

    try:
        document = read_yaml(args.input)
        program = translate_program(document)
    except AssemblyError as error:
        print(f"Assembly error: {error}", file=sys.stderr)
        return 1

    if args.test:
        print_representation(program)
    else:
        print(f"Successfully translated {len(program)} commands.")
        print(
            f"Output path reserved for stage 2: {args.output}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())