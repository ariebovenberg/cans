# 🥫 Canned

🚧 Work in progress 🚧

Composable, robust, functional containers like `Maybe`, `IO`, `Lazy`, `Result`.
Focus on simplicity & predictability 🧩 over fancy ergonomics & magic 🪄.
Supports `mypy`, and pattern matching on Python 3.10+.

## Quickstart

```python
>>> from canned.maybe import Just, Nothing
>>> greeting = Just("hello")
>>> greeting.map(str.upper)
Just("HELLO")

>>> # python 3.10+ only
>>> match greeting:
...     case Just(n):
...         print(f'{greeting.title()} world!')
...     case Nothing():
...         print('Hi world!')
Hello world!
```

Among the supported methods are `flatmap`, `filter`, `zip`, 
as well as the relevant 
[collection APIs](https://docs.python.org/3/library/collections.abc.html).

## Todo

- Docs
- Other containers
- CI/CD
