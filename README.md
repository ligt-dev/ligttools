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
make sure the environment is activated before using the tool.

## For Developers

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

### ligt-search

A simple command-line interface to search for Ligt examples across
local and remote datasets and SPARQL endpoints.
Supports providing additional triples containing local annotations and a table
mapping string labels to external ontologies:

To extract sentences containing glossed GEN from a local Turtle file:
```bash
uv run ligt-search -q ":GEN" test-data.ttl
```

To extract sentences with morph glossed as "cat" and a morph glossed as as "ed" 
and having a value PST
from a remote SPARQL endpoint:
```bash
uv run ligt-search -q "cat ed:PST" http://sparql-endpoint-url/sparql
```

To extract sentences with morph with the form "l" that corresponds to a past tense 
connected to an external ontology from a local data file:
```bash
uv run ligt-search -q "l:<https://purl.org/olia/unimorph/unimorph.owl#PST>" test-data.ttl \
   test-mappings.ttl https://raw.githubusercontent.com/acoli-repo/olia/refs/heads/master/owl/experimental/unimorph/unimorph.owl
```

#### Query syntax

Disclaimer: The query language integrated with the tool is rudimentary and is temporary.
Future integration of the tool into a GUI application and the development of this tool
will lead to significant changes.

The anatomy of a query is the following:
* The query specifies filters on utterances represented in the specified datasets
* Each space-separated token corresponds to a word-like object corresponds to an `ligt:Word` object,
i.e. a word-like token
* The order and co-occurrence is not limited by the query
* Each token has a form of `<form>[:<gloss>]`,
where gloss can be a string literal or a URI in angular brackets

### enligten / ligt-serve

A Flask-based REST API for extracting and converting IGT data from supported formats to RDF 
on-the-fly with `ligt-convert`. Usage:

```bash
# Start the server on default port (8080) and host (0.0.0.0)
enligten

# Start the server on specific host and port
enligten -p 5000 -h 127.0.0.1

# We can also start the server using its alias that is consistent with the rest of the tools:
ligt-serve
```

Calling the API:
```bash
# Convert from CLDF to Ligt
curl "http://localhost:8080/https://raw.githubusercontent.com/cldf-datasets/apics/refs/heads/master/cldf/StructureDataset-metadata.json"

# Convert from CLDF to Ligt with format specified explicitly
curl "http://localhost:8080/https://raw.githubusercontent.com/cldf-datasets/apics/refs/heads/master/cldf/StructureDataset-metadata.json" -H "format: cldf"
```

### Other tools (in development)

- `ligt-validate` - Validates data against the Ligt schema
- `ligt-query` - Query RDF data using SPARQL
- `ligt-visualize` - Visualizes linguistic data structures

## Python API

You can also use LigtTools as a Python library:

### Conversion

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

### Search

Importing the necessary functions and initialising a graph:
```python
from ligttools.search import Dataset
from ligttools.search.sparql import create_graph

datasets = [
    Dataset("test-data.ttl", is_sparql=False),
    Dataset("http://sparql-endpoin-url/sparql", is_sparql=True),
    
    # A dataset can be also initialised from a string
    Dataset.from_string("https://remote.url/dataset.ttl")
]

g = create_graph(datasets)
```

Now we can define the arguments and run the query:
```python
from ligttools.search import QueryArg
from ligttools.search.sparql import get_results

args = [
    QueryArg("s", "PL", is_uri=False),
    QueryArg(None, "NOM"),
    QueryArg(None, "<https://purl.org/olia/unimorph/unimorph.owl#PST>", is_uri=True),
    
    # An argument can also be parsed from a string
    QueryArg.from_token(":PST")
]

# We need to explicitly provide a list of remote SPARQL endpoints
endpoints = [ds.url for ds in datasets if ds.is_sparql]
for row in get_results(g, endpoints, args):
    print(row)
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