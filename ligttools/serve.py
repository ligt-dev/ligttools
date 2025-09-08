import argparse
from flask import Flask, Response, request
from ligttools.converters import get_converter

app = Flask(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="A small web server for converting IGT data to RDF on-the-fly"
    )
    parser.add_argument('-p', '--port', type=int, default=8080,
                        help='Port to run the server on (default: 8080)')
    parser.add_argument('-H', '--host', default='0.0.0.0',
                        help='Host to run the server on (default: 0.0.0.0)')
    parser.add_argument('--version', action='version', version='%(prog)s 0.3.1',
                        help='Show version information and exit')
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    app.run(host=args.host, port=args.port)


@app.route("/<path:source_url>")
def convert(source_url: str):
    format_name = request.args.get('format', 'cldf')
    try:
        converter = get_converter(format_name)
        output = converter.to_rdf(source_url)
    except ValueError as e:
        return Response(f"Error: {str(e)}", status=400, mimetype="text/plain")
    except Exception as e:
        return Response(f"Error: {str(e)}", status=500, mimetype="text/plain")
    return Response(output, mimetype="text/turtle")


if __name__ == "__main__":
    main()
