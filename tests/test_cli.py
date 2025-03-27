"""
Tests for the CLI module.
"""
import os
import tempfile
from unittest import mock

import pytest
from ligttools.cli import create_parser, main


class TestCli:
    """Test CLI functionality."""

    def test_create_parser(self):
        """Test parser creation."""
        parser = create_parser()
        assert parser is not None

    def test_list_formats(self):
        """Test listing formats."""
        with mock.patch('sys.stdout') as mock_stdout:
            # Call with --list-formats
            args = ['--list-formats']
            exit_code = main(args)

            # Check that it succeeded
            assert exit_code == 0

            # Check that stdout was called with the list of formats
            output = mock_stdout.write.call_args_list
            assert any('Supported formats:' in str(args) for args in output)
            assert any('json' in str(args) for args in output)
            assert any('csv' in str(args) for args in output)

    def test_missing_format_args(self):
        """Test error for missing format arguments."""
        with mock.patch('sys.stderr'):
            # Call without required args
            with pytest.raises(SystemExit):
                parser = create_parser()
                parser.parse_args(['-f', 'json'])

            with pytest.raises(SystemExit):
                parser = create_parser()
                parser.parse_args(['-t', 'rdf'])

    def test_conversion_json_to_rdf(self):
        """Test converting JSON to RDF."""
        # Create a temp JSON file
        json_content = '{"test": "data"}'
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            temp_file.write(json_content.encode('utf-8'))
            json_path = temp_file.name

        # Create a temp output file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.rdf') as out_file:
            out_path = out_file.name

        try:
            # Call the CLI
            args = ['-f', 'json', '-t', 'rdf', json_path, '-o', out_path]
            exit_code = main(args)

            # Check that it succeeded
            assert exit_code == 0
            assert os.path.exists(out_path)

            # Check file content
            with open(out_path, 'r') as f:
                content = f.read()
                assert 'test' in content
                assert 'data' in content

        finally:
            # Clean up
            if os.path.exists(json_path):
                os.unlink(json_path)
            if os.path.exists(out_path):
                os.unlink(out_path)

    def test_invalid_format(self):
        """Test error for invalid format."""
        with mock.patch('sys.stderr'):
            # Call with invalid format
            args = ['-f', 'invalid', '-t', 'rdf', 'test.txt']
            exit_code = main(args)

            # Should return error code
            assert exit_code == 1
