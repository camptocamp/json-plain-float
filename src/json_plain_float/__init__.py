# Copyright 2026 Camptocamp SA
# License MIT (https://opensource.org/licenses/MIT)
"""JSON encoding with floats in plain decimal notation, never in scientific notation."""

from .encoder import PlainFloatJSONEncoder, dump, dumps, format_float

__all__ = ["PlainFloatJSONEncoder", "dump", "dumps", "format_float"]
