"""
Base converter module that defines the interface for all converters.
"""
from abc import ABC, abstractmethod

class BaseConverter(ABC):
    """Base class for all converters with common functionality."""

    @abstractmethod
    def to_rdf(self, input_data, output_path=None, serialization='ttl'):
        """Convert input data to RDF format."""
        pass

    @abstractmethod
    def from_rdf(self, input_data, output_path=None, serialization='ttl'):
        """Convert RDF data to the target format."""
        pass
