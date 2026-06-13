# singleflight

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Zero dependencies](https://img.shields.io/badge/dependencies-0-brightgreen.svg)](#)

Collapse concurrent **duplicate** calls into a single execution. When N callers request
the same key at once, only **one** does the work — the rest wait and share its result.
The classic guard against cache stampedes and thundering herds. Zero dependencies.

## Install
```bash
pip install singleflight
```

## Use
```python
from singleflight import Group

g = Group()

def expensive():
    return fetch_from_db()

value, shared = g.do("user:42", expensive)
# 100 concurrent callers for "user:42" -> expensive() runs ONCE,
# all 100 get the same value; `shared` is True for the 99 that waited.
```

## Features
- ✅ One execution per key under concurrency; others share the result
- ✅ Errors propagate to every waiter
- ✅ Different keys run independently
- ✅ `forget(key)` to drop an in-flight entry
- ✅ **Zero dependencies**

## License
MIT © WCN Development Co
