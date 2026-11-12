# json-plain-float

JSON encoding with floats in plain decimal notation, never in scientific notation.

Python's `json` writes small and large floats with an exponent (`2e-06`, `1e+22`).
That is valid JSON, but some parsers reject it. This package writes `0.000002`
and `10000000000000000000000.0` instead:

- floats stay JSON numbers;
- each float gets the shortest digits that read back as the same value
  (`0.1 + 0.2` is still `0.30000000000000004`, `2.5` is still `2.5`);
- everything else is encoded exactly like the standard library does, with the
  same options (`ensure_ascii`, `indent`, `sort_keys`, `default`, `allow_nan`, ...).

No dependencies. Python 3.10 to 3.14, the versions supported by Odoo 18.0, 19.0
and 20.0.

## Usage

```python
import json
from json_plain_float import PlainFloatJSONEncoder, dumps

dumps({"weight_kg": 0.000002})
# '{"weight_kg": 0.000002}'

json.dumps({"weight_kg": 0.000002}, cls=PlainFloatJSONEncoder, ensure_ascii=False)
# '{"weight_kg": 0.000002}'
```

`dump(obj, fp, **kwargs)` writes to a file, and `format_float(value)` formats a
single float.

## How it works

The standard library offers no hook for float formatting: both its C and
Python encoders call `float.__repr__` directly. `PlainFloatJSONEncoder`
rebuilds the encoding loop of `json.JSONEncoder.iterencode` with the
pure-Python encoder and its own float formatter. It relies on the private
`json.encoder._make_iterencode`, covered by the tests on every supported
Python version, and it is slower than the C encoder.

Other options considered: no JSON library on PyPI offers this (`simplejson`,
`orjson`, `ujson`, `python-rapidjson` all write an exponent); `fujson`
formats floats with a fixed number of decimals and patches the `json` module
globally while encoding; converting floats to `Decimal` still gives `1E-7`
below 1e-6.

## Development

```bash
uv run --group test pytest        # current Python
uvx --with tox-uv tox             # Python 3.10 to 3.14, plus lint
```

tox-uv downloads the missing Python versions.

## Credits

Authors:

- Iván Todorovich <ivan.todorovich@camptocamp.com>
- Simone Orsi <simone.orsi@camptocamp.com>

Maintained by [Camptocamp](https://www.camptocamp.com).
