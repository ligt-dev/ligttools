#!/usr/bin/env python3
import argparse
import sys
from typing import List, Optional

from ligttools.converters import get_converter, get_supported_formats


def convert_command(args):
    """Handle the conversion between formats"""
    try:
        # Determine if we're converting to or from RDF
        if args.from_format.lower() == 'rdf':
            
            # Converting from RDF to another format
            print(f"Preparing conversion from Ligt to {args.to_format.upper()}...")
            converter = get_converter(args.to_format)
            print(f"Starting the conversion process...")
            serialization = args.to_format.split('.')[-1] if '.' in args.to_format else None
            converter.from_rdf(args.input_file, args.output, serialization=serialization)
            print(f"Converted from RDF to {args.to_format.upper()}")
        else:
            # Converting from another format to RDF
            print(f"Preparing conversion from {args.from_format.upper()} to Ligt...")
            converter = get_converter(args.from_format)
            print(f"Starting the conversion process...")
            serialization = args.from_format.split('.')[-1] if '.' in args.from_format else None
            converter.to_rdf(args.input_file, args.output, serialization=serialization)
            print(f"Converted from {args.from_format.upper()} to RDF")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0



def list_formats_command():
    """List all supported formats"""
    formats = get_supported_formats()
    print("Supported formats:")
    for fmt in formats:
        print(f"- {fmt}")


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Convert data between different formats and RDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert examples from a CLDF dataset to Ligt
  ligttools -f cldf -t rdf examples.cldf -o output.ttl

  # Convert from Ligt to CLDF
  ligttools -f rdf -t json input.rdf -o output.json

  # List supported formats
  ligttools --list-formats
""")

    # Add arguments for input/output files
    parser.add_argument('input_file', nargs='?',
                        help='Input file to convert (omit to read from stdin)')

    parser.add_argument('-o', '--output',
                        help='Output file (defaults to stdout)')

    # Add format specification arguments
    parser.add_argument('-f', '--from', dest='from_format',
                        help='Source format of the input file')

    parser.add_argument('-t', '--to', dest='to_format',
                        help='Target format for the output file')

    # Add utility flags
    parser.add_argument('--list-formats', action='store_true',
                        help='List all supported formats and exit')

    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0',
                        help='Show version information and exit')

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the CLI application"""
    parser = create_parser()
    args = parser.parse_args(argv)

    # Handle list-formats command first
    if args.list_formats:
        list_formats_command()
        return 0

    # Check required arguments for conversion
    if not args.from_format and not args.to_format:
        parser.error("Either --from or --to format must be specified")

    # Defaults to Ligt
    if not args.from_format:
        args.from_format = 'rdf'

    # Defaults to Ligt
    if not args.to_format:
        args.to_format = 'rdf'

    # Handle stdin for input if no file provided
    if not args.input_file:
        # Read from stdin
        args.input_file = sys.stdin

    # Handle conversion
    return convert_command(args)


if __name__ == '__main__':
    sys.exit(main())
