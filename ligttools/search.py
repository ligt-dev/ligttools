import argparse
import sys
import re

from ligttools.search import QueryArg, Dataset
from ligttools.search.sparql import get_results, create_graph


def parse_query(query: str):
    tokens = re.split(r"\s+", query)
    return [QueryArg.from_token(tok) for tok in tokens]

def parse_datasets(datasets: list[str]):
    parsed_datasets = [ds for ds_str in datasets if (ds := Dataset.from_string(ds_str)) is not None]
    for ds in parsed_datasets:
        print("Detected dataset:", ds)
    return parsed_datasets

def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Search for examples in Ligt datasets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract sentences containing glossed NOM from a local Turtle file data.ttl
  ligt-search -q ":NOM" data.ttl

  # Extract sentences with a morph glossed as "cat" and a morph glossed as "-ed" 
  # and having a value PST from a remote SPARQL endpoint
  ligt-search -q "cat ed:PST" http://sparql-endpoint-url/sparql

  # Extract sentences with morph glossed as "-s" and that corresponds to a plural 
  # connected to an external ontology from a local data file
  ligt-search -q "s:<https://purl.org/olia/unimorph.owl#PL>" data.ttl mappings.ttl https://purl.org/olia/unimorph.owl
""")

    parser.add_argument(
        "-q", "--query",
        required=True,
        help="A query string to be processed"
    )

    parser.add_argument('-o', '--output',
                        help='Output file (defaults to stdout)')

    parser.add_argument(
        "datasets",
        metavar="dataset",
        nargs="+",
        help="Local RDF files or remote RDF files or SPARQL endpoints"
    )

    parser.add_argument('--version', action='version', version='%(prog)s 0.3.0',
                        help='Show version information and exit')

    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

    query_args = parse_query(args.query)
    datasets = parse_datasets(args.datasets)
    endpoints = [ds.url for ds in datasets if ds.is_sparql]

    with open(args.output, "w") if args.output else sys.stdout as out_file:
        for res in get_results(create_graph(datasets), endpoints, query_args):
            out_file.write(res + "\n")

if __name__ == "__main__":
    main()
