# ligttools

A collection of tools for converting IGT (Interlinear Glossed Text) data between different formats, including Ligt, an RDF specification.

## Overview

_ligttools_ is a Python library and collection of command-line tools 
for working with Interlinear Glossed Text in RDF. 
It provides utilities for converting data between various commonly used formats (ToolBox, FLEx, etc.) 
and RDF (Resource Description Framework) using Ligt vocabulary.

## Installation

Install ligttools using pip:

```bash
git clone https://github.com/ligt-dev/ligttools.git
pip install .
```

After installing the package, a command-line tool `ligt-convert`
will be available in your system.

If you installed the package in a virtual environment,
make sure the environment is activated before to use the tool.

### For Developers

For development, we recommend using [uv](https://docs.astral.sh/uv/).
To set up the environment:

```bash
# Clone the repository
git clone https://github.com/ligt-dev/ligttools.git
cd ligttools
uv sync

# For development dependencies (testing, etc.)
uv sync --extra dev
```


## Available Tools

### ligt-convert

A tool for converting data between common IGT data formats and RDF-based Ligt:

```bash
# Convert from CLDF to Ligt
ligt-convert -f cldf -t ligt input.json -o output.rdf

# Convert from Ligt to Toolbox 
ligt-convert -f ligt -t toolbox input.rdf -o output.json

# You can also use long-form flags:
ligt-convert --from=cldf --to=ligt examples.csv --output=examples.ttl

# List supported formats
ligt-convert --list-formats
```

For advanced usage:

```bash
# Read from stdin (specify input format explicitly)
cat input.json | ligt-convert -f cldf -t ligt -o output.ttl

# Write to stdout (omit the output file)
ligt-convert -f cldf -t ligt examples.csv

# Specify RDF serialisation (default is Turtle)

ligt-convert -f cldf -t ligt.n3 examples.csv
```

### Other tools (in development)

- `ligt-validate` - Validates data against the Ligt schema
- `ligt-query` - Query RDF data using SPARQL
- `ligt-visualize` - Visualizes linguistic data structures

### Python API

You can also use LigtTools as a Python library:

```python
from ligttools.converters import get_converter

# Convert JSON to RDF
cldf_converter = get_converter('cldf')
rdf_data = cldf_converter.to_rdf('examples.csv', 'output.ttl')

# Convert RDF to JSON
json_data = cldf_converter.from_rdf('input.ttl', 'output.csv')

# Get list of supported formats
from ligttools.converters import get_supported_formats
formats = get_supported_formats()
```

## Supported Formats

Currently, ligttools supports the following formats:

- CLDF
- ToolBox
- FLExText

## Extending ligttools

To add support for a new format:

1. Create a new converter class that extends `BaseConverter`
2. Implement the `to_rdf` and `from_rdf` methods
3. Register the converter using the registration function

Example:

```python
from ligttools.converters.base import BaseConverter
from ligttools.converters import register_converter

class ELANConverter(BaseConverter):
    def to_rdf(self, input_data, output_path=None):
        # Implementation...
        pass

    def from_rdf(self, input_data, output_path=None):
        # Implementation...
        pass

# Register the converter
register_converter('xml', ELANConverter)
```

## License

This software is licensed under the [MIT License](LICENSE).