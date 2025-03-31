"""
Toolbox to Ligt converter
"""

from ligttools.converters.base import BaseConverter

class ToolboxConverter(BaseConverter):
    """Converter for CLDF format."""

    def to_rdf(self, input_data, output_path=None, serialization='ttl'):
        raise NotImplementedError("Toolbox -> RDF is not supported yet.")

    def from_rdf(self, input_data, output_path=None, serialization='ttl'):
        raise NotImplementedError("RDF -> Toolbox is not supported yet.")