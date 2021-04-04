# 🥫 Canned

(🚧 Work in progress 🚧)

Composable, functional containers like `Maybe`, `IO`, `Lazy`, `Result`.
Focus on simplicity & predictability 🧩 over fancy ergonomics & magic 🪄.
Supports `mypy`, and even pattern matching on Python 3.10+.

## Quickstart

```python
>>> from canned.maybe import Just, Nothing
>>> m = Just("world")
>>> m.map(str.upper)
Just("WORLD")
>>> m.unwrap()
"WORLD"
>>> # python 3.10+ only
>>> match m:
...     case Just(n):
...         print(f'Hello {n.title()}!')
...     case Nothing():
...         print('Nope.')
Hello World!
```

Among the supported methods are `flatmap`, `filter`, `zip`, 
as well as the relevant collection APIs.

## Todo

- Docs
- Other containers
- CI/CD
