# converters/__init__.py
"""Converter registry and loader module."""
from typing import Dict, Type

from ligttools.converters.base import BaseConverter
from ligttools.converters.cldf_converter import CLDFConverter
from ligttools.converters.toolbox_converter import ToolboxConverter
from ligttools.converters.flex_converter import FlexConverter

# Registry of available converters
_CONVERTER_REGISTRY: Dict[str, Type[BaseConverter]] = {}


# Register built-in converters
def register_converter(format_name: str, converter_class: Type[BaseConverter]) -> None:
    """Register a converter for a specific format."""
    _CONVERTER_REGISTRY[format_name.lower()] = converter_class


def get_converter(format_name: str) -> BaseConverter:
    """Get a converter instance for the specified format."""
    format_name = format_name.lower()
    if format_name not in _CONVERTER_REGISTRY:
        supported = ", ".join(_CONVERTER_REGISTRY.keys())
        raise ValueError(f"Unsupported format: {format_name}. Supported formats: {supported}")
    return _CONVERTER_REGISTRY[format_name]()


def get_supported_formats() -> list[str]:
    """Get a list of supported formats."""
    return list(_CONVERTER_REGISTRY.keys())


# Register built-in converters
register_converter('cldf', CLDFConverter)
register_converter('toolbox', ToolboxConverter)
register_converter('flex', FlexConverter)
