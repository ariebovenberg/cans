# 🍡 Dango

Work in progress 🚧.

Composable, functional containers like `Maybe`, `IO`, `Lazy`, `Result`.
Focus on simplicity & predictability 🧩 over fancy ergonomics & magic 🪄.

## Quickstart

```python
>>> from dango import maybe
>>> m = maybe.of("foo")
Just("foo")
>>> m.map(str.upper)
Just("FOO")
>>> m.unwrap()
"FOO"
```

Among the supported methods are `flatmap`, `filter`, `zip`.
