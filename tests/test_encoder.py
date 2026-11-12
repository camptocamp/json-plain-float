# Copyright 2026 Camptocamp SA
# @author Iván Todorovich <ivan.todorovich@camptocamp.com>
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License MIT (https://opensource.org/licenses/MIT)
import io
import json
import math
import random

import pytest

from json_plain_float import PlainFloatJSONEncoder, dump, dumps, format_float


def test_small_float_in_decimal_notation():
    """A small float is written in decimal notation, not as ``2e-06``."""
    assert dumps({"weight_kg": 0.000002}) == '{"weight_kg": 0.000002}'


def test_large_float_in_decimal_notation():
    """A large float is written in full, not as ``1e+22``, and stays a float."""
    assert dumps(1e22) == "10000000000000000000000.0"
    assert isinstance(json.loads(dumps(1e22)), float)


@pytest.mark.parametrize(
    "value, expected",
    [
        (1e-07, "0.0000001"),
        (1.5e-10, "0.00000000015"),
        (-2e-06, "-0.000002"),
        (0.1 + 0.2, "0.30000000000000004"),
        (2.5, "2.5"),
        (10.0, "10.0"),
        (0.0, "0.0"),
        (-0.0, "-0.0"),
        (1e16, "10000000000000000.0"),
    ],
)
def test_format_float(value, expected):
    """Floats get the shortest exact digits, without exponent."""
    assert format_float(value) == expected


def test_other_values_unchanged():
    """Every other value is encoded like the stdlib encoder does."""
    payload = {"weight_kg": 2.5, "quantity": 10.0, "position": 3, "name": "Zürich"}
    assert dumps(payload, ensure_ascii=False) == json.dumps(payload, ensure_ascii=False)


def test_options_kept():
    """Encoder options such as ``ensure_ascii``, ``sort_keys``, ``indent`` apply."""
    payload = {"b": 0.00001, "a": "Zürich", "c": [1, None, True]}
    expected = '{"a": "Z\\u00fcrich", "b": 0.00001, "c": [1, null, true]}'
    assert dumps(payload, sort_keys=True) == expected
    assert dumps(payload, indent=2) == json.dumps(payload, indent=2).replace(
        "1e-05", "0.00001"
    )


def test_default_hook():
    """Values handled by ``default`` are encoded as with the stdlib."""
    assert dumps({"d": {1, 2}}, default=sorted) == '{"d": [1, 2]}'


def test_cls_usage():
    """The encoder works as ``cls`` of ``json.dumps``."""
    assert json.dumps([2e-06], cls=PlainFloatJSONEncoder) == "[0.000002]"


def test_dump_to_file():
    """``dump`` writes the same text as ``dumps``."""
    fp = io.StringIO()
    dump({"x": 1e-07}, fp)
    assert fp.getvalue() == '{"x": 0.0000001}'


def test_round_trip():
    """Any finite float reads back as the same value."""
    rnd = random.Random(42)
    values = [rnd.uniform(-1, 1) * 10 ** rnd.randint(-20, 20) for _ in range(2000)]
    values += [5e-324, 1.7976931348623157e308, -0.0]
    text = dumps(values)
    assert "e" not in text.lower()
    loaded = json.loads(text)
    assert loaded == values
    assert all(isinstance(value, float) for value in loaded)


def test_nan_and_infinity_like_stdlib():
    """NaN and infinity follow ``allow_nan`` like the stdlib encoder."""
    values = [math.nan, math.inf, -math.inf]
    assert dumps(values) == json.dumps(values)
    with pytest.raises(ValueError):
        dumps(values, allow_nan=False)


def test_circular_reference_detected():
    """Circular references raise like with the stdlib encoder."""
    data = []
    data.append(data)
    with pytest.raises(ValueError, match="Circular reference"):
        dumps(data)
