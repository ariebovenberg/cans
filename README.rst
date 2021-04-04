🥫 Canned
=========

.. image:: https://img.shields.io/pypi/v/canned.svg?style=flat-square
   :target: https://pypi.python.org/pypi/canned

.. image:: https://img.shields.io/pypi/l/canned.svg?style=flat-square
   :target: https://pypi.python.org/pypi/canned

.. image:: https://img.shields.io/pypi/pyversions/canned.svg?style=flat-square
   :target: https://pypi.python.org/pypi/canned

.. image:: https://img.shields.io/readthedocs/canned.svg?style=flat-square
   :target: http://canned.readthedocs.io/

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square
   :target: https://github.com/psf/black

Composable, robust, functional containers like ``Maybe``.
Properly typed and supports pattern matching on Python 3.10+.

Quickstart
----------

.. code-block:: python3

   >>> from canned import Just, Nothing
   >>> greeting = Just("hello")
   >>> greeting.map(str.upper)
   Just("HELLO")
   ...
   >>> # Python 3.10+ only
   >>> match greeting:
   ...     case Just(n):
   ...         print(f"{greeting.title()} world!")
   ...     case Nothing():
   ...         print("Hi world!")
   Hello world!

Among the supported methods are ``flatmap``, ``filter``, ``zip``,
as well as the relevant
`collection APIs <https://docs.python.org/3/library/collections.abc.html>`_.

Todo
----

- Other containers
