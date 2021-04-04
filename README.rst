🥫 Canned
=========

🚧 Work in progress 🚧

Composable, robust, functional containers like ``Maybe``, ``IO``, ``Lazy``, ``Result``.
Properly typed and supports pattern matching on Python 3.10+.

Quickstart
----------

.. code-block:: python3

   >>> from canned import Just, Nothing
   >>> greeting = Just("hello")
   >>> greeting.map(str.upper)
   Just("HELLO")

   >>> # Python 3.10+ only
   >>> match greeting:
   ...     case Just(n):
   ...         print(f'{greeting.title()} world!')
   ...     case Nothing():
   ...         print('Hi world!')
   Hello world!

Among the supported methods are ``flatmap``, ``filter``, ``zip``,
as well as the relevant
`collection APIs <https://docs.python.org/3/library/collections.abc.html>`_.

Todo
----

- Other containers
- CI/CD
