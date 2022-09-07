🥫 Cans
=======

.. image:: https://img.shields.io/pypi/v/cans.svg?style=flat-square
   :target: https://pypi.python.org/pypi/cans

.. image:: https://img.shields.io/pypi/l/cans.svg?style=flat-square
   :target: https://pypi.python.org/pypi/cans

.. image:: https://img.shields.io/pypi/pyversions/cans.svg?style=flat-square
   :target: https://pypi.python.org/pypi/cans

.. image:: https://img.shields.io/readthedocs/cans.svg?style=flat-square
   :target: http://cans.readthedocs.io/

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square
   :target: https://github.com/psf/black

Simple, functional, composable containers like ``Maybe``.
Properly **typed** and supports **pattern matching** on Python 3.10+.
Inspired by the containers in the `Rust standard library <https://doc.rust-lang.org/std/option/>`_.
They're also proper Python citizens with nice ``repr`` and picklability.

Why?
----

In contrast to other libraries,
``cans`` focusses on rigorous simplicity and offers:

- **Typing** compatible with all type checkers (not only ``mypy``)
- **Stable** and semantically versioned API
- **Simple** code with no magic or clever hacks

Quickstart
----------

.. code-block:: python3

   >>> from cans import Some, Nothing, Maybe
   ...
   >>> def first(m: list[str]) -> Maybe[str]:
   ...     return Some(m[0]) if m else Nothing()
   ...
   >>> greeting = first(["hello", "hi", "howdy"]).map(str.title)
   Some("Hello")
   ...
   >>> # Python 3.10+ only
   >>> match greeting:
   ...     case Some(n):
   ...         print(f"{greeting} world!")
   ...     case Nothing():
   ...         print("Hi there!")
   Hello world!

Among the supported methods are ``flatmap``, ``filter``, ``zip``,
as well as the relevant
`collection APIs <https://docs.python.org/3/library/collections.abc.html>`_.
See `the documentation <https://cans.readthedocs.io>`_ for a complete overview.

Todo
----

- Other containers
