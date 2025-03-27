"""
Tests for the converters module.
"""
import os
import tempfile
import pytest

from ligttools.converters import get_converter, register_converter, get_supported_formats
from ligttools.converters.base import BaseConverter
from ligttools.converters.json_converter import JsonConverter


class TestConverters:
    """Test converter functionality."""

    def test_get_converter(self):
        """Test getting converters."""
        # Get a valid converter
        json_converter = get_converter('json')
        assert isinstance(json_converter, JsonConverter)

        # Test case insensitivity
        json_converter = get_converter('JSON')
        assert isinstance(json_converter, JsonConverter)

        # Test invalid converter
        with pytest.raises(ValueError):
            get_converter('invalid_format')

    def test_register_converter(self):
        """Test registering a new converter."""

        # Create a mock converter
        class MockConverter(BaseConverter):
            def to_rdf(self, input_data, output_path=None):
                return "mock_rdf"

            def from_rdf(self, input_data, output_path=None):
                return {"mock": "data"}

        # Register the converter
        register_converter('mock', MockConverter)

        # Verify it was registered
        supported_formats = get_supported_formats()
        assert 'mock' in supported_formats

        # Get the converter and use it
        mock_converter = get_converter('mock')
        assert isinstance(mock_converter, MockConverter)
        assert mock_converter.to_rdf('dummy') == "mock_rdf"

    def test_json_converter_to_rdf(self):
        """Test converting JSON to RDF."""
        # Create a temp JSON file
        json_content = '{"test": "data"}'
        with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as temp_file:
            temp_file.write(json_content.encode('utf-8'))
            json_path = temp_file.name

        try:
            # Convert to RDF
            converter = get_converter('json')
            rdf_output = converter.to_rdf(json_path)

            # Check that it contains our test data
            assert 'test' in rdf_output
            assert 'data' in rdf_output

            # Test with output file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.rdf') as out_file:
                out_path = out_file.name

            try:
                converter.to_rdf(json_path, out_path)
                assert os.path.exists(out_path)
                with open(out_path, 'r') as f:
                    content = f.read()
                    assert 'test' in content
                    assert 'data' in content
            finally:
                if os.path.exists(out_path):
                    os.unlink(out_path)

        finally:
            if os.path.exists(json_path):
                os.unlink(json_path)

    def test_json_converter_from_rdf(self):
        """Test converting RDF to JSON."""
        # Create a temp RDF file (mock)
        rdf_content = "# RDF data"
        with tempfile.NamedTemporaryFile(delete=False, suffix='.rdf') as temp_file:
            temp_file.write(rdf_content.encode('utf-8'))
            rdf_path = temp_file.name

        try:
            # Convert to JSON
            converter = get_converter('json')
            json_output = converter.from_rdf(rdf_path)

            # Check the output structure
            assert isinstance(json_output, dict)
            assert 'example' in json_output

            # Test with output file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as out_file:
                out_path = out_file.name

            try:
                converter.from_rdf(rdf_path, out_path)
                assert os.path.exists(out_path)
                with open(out_path, 'r') as f:
                    content = f.read()
                    assert 'example' in content
            finally:
                if os.path.exists(out_path):
                    os.unlink(out_path)

        finally:
            if os.path.exists(rdf_path):
                os.unlink(rdf_path)

    def test_get_supported_formats(self):
        """Test getting supported formats."""
        supported_formats = get_supported_formats()
        assert isinstance(supported_formats, list)
        assert 'json' in supported_formats
        assert 'csv' in supported_formats
