"""
FLExText to Ligt converter
"""
from cldflex import flex2csv
from pathlib import Path
from ligttools.converters.base import BaseConverter
from ligttools.converters.cldf_converter import CLDFConverter

import tempfile

class FlexConverter(BaseConverter):
    """Converter for CLDF format."""

    def to_rdf(self, input_data, output_path=None, serialization='ttl'):
        temp_dir = tempfile.TemporaryDirectory()

        input_data = Path(input_data)
        dataset = flex2csv.convert(input_data, output_dir=Path(temp_dir.name))

        return CLDFConverter().to_rdf("examples.csv", output_path=Path(output_path) if output_path else None)

    def from_rdf(self, input_data, output_path=None, serialization='ttl'):
        raise NotImplementedError("RDF -> FLEx is not supported yet.")