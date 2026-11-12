# Copyright 2026 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License MIT (https://opensource.org/licenses/MIT)
"""JSON encoder writing floats in plain decimal notation."""

import json
from decimal import Decimal


def format_float(value):
    """Format ``value`` in plain decimal notation, with the shortest exact digits.

    ``repr`` gives the shortest digits that read back as the same float (no
    ``0.30000000000000004`` noise), and ``Decimal`` writes them without an
    exponent: 2e-06 -> "0.000002", 2.5 -> "2.5", 10.0 -> "10.0". A decimal
    point is always kept, so that the value reads back as a float: 1e+22 ->
    "10000000000000000000000.0", not an integer.
    """
    text = format(Decimal(repr(value)), "f")
    if "." not in text:
        text += ".0"
    return text


class PlainFloatJSONEncoder(json.JSONEncoder):
    """JSON encoder that never writes floats in scientific notation.

    The stdlib encoder writes small floats like ``2e-06``, which some parsers
    reject: this encoder writes ``0.000002`` instead. Floats are still written
    as JSON numbers, and every other value is encoded as usual. NaN and
    infinity follow ``allow_nan`` like the stdlib.

    Use it as ``json.dumps(payload, cls=PlainFloatJSONEncoder)``.
    """

    def iterencode(self, o, _one_shot=False):
        """Encode ``o`` like the stdlib, with floats in plain decimal notation."""
        # ``JSONEncoder.iterencode`` writes floats with ``float.__repr__``, which
        # switches to scientific notation below 1e-4. There is no option to change
        # that, and float subclasses don't help either: both the C and the Python
        # encoder call ``float.__repr__`` directly, ignoring any override.
        #
        # What we can change is the float formatter itself. ``iterencode`` builds
        # its encoding loop with ``_make_iterencode`` (the pure-Python encoder),
        # passing the formatter as the ``floatstr`` argument. So we do the same as
        # ``iterencode``, minus the C encoder shortcut, with our own formatter.
        allow_nan = self.allow_nan
        # Python 3.13+ converts an integer indent to spaces before calling
        # ``_make_iterencode``, which no longer does it; older versions accept
        # both. Passing spaces works everywhere.
        indent = self.indent
        if indent is not None and not isinstance(indent, str):
            indent = " " * indent

        def floatstr(value):
            """Format ``value`` like the stdlib, finite values without exponent."""
            if value != value:
                text = "NaN"
            elif value == float("inf"):
                text = "Infinity"
            elif value == float("-inf"):
                text = "-Infinity"
            else:
                return format_float(value)
            if not allow_nan:
                raise ValueError(
                    "Out of range float values are not JSON compliant: " + repr(value)
                )
            return text

        return json.encoder._make_iterencode(
            {} if self.check_circular else None,
            self.default,
            (
                json.encoder.encode_basestring_ascii
                if self.ensure_ascii
                else json.encoder.encode_basestring
            ),
            indent,
            floatstr,
            self.key_separator,
            self.item_separator,
            self.sort_keys,
            self.skipkeys,
            _one_shot,
        )(o, 0)


def dumps(obj, **kwargs):
    """Serialize ``obj`` like ``json.dumps``, with floats in plain decimal notation."""
    return json.dumps(obj, cls=PlainFloatJSONEncoder, **kwargs)


def dump(obj, fp, **kwargs):
    """Serialize ``obj`` to ``fp`` like ``json.dump``, with plain decimal floats."""
    return json.dump(obj, fp, cls=PlainFloatJSONEncoder, **kwargs)
