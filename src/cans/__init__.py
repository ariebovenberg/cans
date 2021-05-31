from __future__ import annotations
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Generic,
    Iterator,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    overload,
)

from typing_extensions import TypeGuard, final

# Single-sourcing the version number with poetry:
# https://github.com/python-poetry/poetry/pull/2366#issuecomment-652418094
try:
    __version__ = __import__("importlib.metadata").metadata.version(__name__)
except ModuleNotFoundError:  # pragma: no cover
    __version__ = __import__("importlib_metadata").version(__name__)

__all__ = [
    "Maybe",
    "Some",
    "Nothing",
    "Lazy",
]

T = TypeVar("T", covariant=True)
U = TypeVar("U", covariant=True)
V = TypeVar("V")


class Maybe(Sequence[T]):
    """
    A container which contains either one item, or none.
    Use :class:`~cans.Some` and :class:`~cans.Nothing` to express
    these two variants.
    When type annotating, only use :data:`~cans.Maybe`.

    >>> a: Maybe[int] = Some(5)
    >>> b: Maybe[str] = Nothing()
    ...
    >>> def parse(s: str) -> Maybe[int]:
    ...     try: return Some(int(s))
    ...     except ValueError: return Nothing()
    ...
    >>> def first(m: list[T]) -> Maybe[T]:
    ...     return Some(m[0]) if m else Nothing()
    ...
    >>> parse("42")
    Some(42)
    >>> first([])
    Nothing()

    Various methods are available (documented in :class:`~cans.Maybe`)
    which you can use to operate on the value, without repeatedly unpacking it.

    >>> first(["-5", "6", ""]).flatmap(parse).map(abs)
    Some(5)
    >>> first([]).flatmap(parse).map(abs).unwrap_or("Nothing here...")
    "Nothing here..."

    In Python 3.10+, you can use pattern matching to deconstruct
    a :class:`~cans.Maybe`.

    >>> match first(["bob", "henry", "anita"]).map(str.title):
    ...     case Some(x):
    ...         print(f'Hello {x}!')
    ...     case Nothing()
    ...         print('Nobody here...')
    "Hello Bob!"

    :class:`~cans.Maybe` also implements the
    :class:`~collections.abc.Sequence` API,
    meaning it acts kind of like a list with one or no items.
    Thus, it works nicely with :mod:`itertools`!

    >>> from itertools import chain
    >>> list(chain.from_iterable(map(parse, "a4f59b")))
    [4, 5, 9]
    """

    __slots__ = ()

    def __init__(self) -> None:
        raise TypeError(
            "Can't instantiate Maybe directly. "
            "Use the factory methods `of` and `from_optional` instead."
        )

    @final
    @staticmethod
    def from_optional(_v: Optional[T]) -> Maybe[T]:
        """Create a maybe container from a value which may be ``None``.
        In that case, it'll be an empty Maybe.

        Example
        -------

        >>> Maybe.from_optional(5)
        Some(5)
        >>> Maybe.from_optional(None)
        Nothing()
        """
        return _NOTHING if _v is None else Some(_v)

    def flatten(self: Maybe[Maybe[U]]) -> Maybe[U]:
        """Flatten a nested container.

        Example
        -------

        >>> Maybe.flatten(Some(Some(5)))
        Some(5)
        >>> Maybe.flatten(Some(Nothing()))
        Nothing()
        >>> Maybe.flatten(Nothing())
        Nothing()
        """
        raise NotImplementedError()

    def unwrap(self) -> T:
        """Unwrap the value in this container.
        If there is no value, :class:`TypeError` is raised.

        Example
        -------

        >>> Some(6).unwrap()
        6
        >>> Nothing().unwrap()
        Exception: TypeError()

        Tip
        ---

        Only use this if you're absolutely sure that there is a value.
        If not, use :meth:`~cans.Maybe.unwrap_or` instead.
        Or, use :meth:`~cans.Maybe.expect`
        for a more descriptive message.
        """
        raise NotImplementedError()

    def unwrap_or(self, _default: V) -> Union[T, V]:
        """Unwrap the value in this container.
        If there is no value, return the given default.

        Example
        -------

        >>> Some(8).unwrap_or("foo")
        8
        >>> Nothing().unwrap_or("foo")
        "foo"
        """
        raise NotImplementedError()

    def expect(self, _msg: str) -> T:
        """Unwrap the value in this container.
        If there is no value, raise an AssertionError with message

        >>> Some(9).expect("What on earth?")
        9
        >>> Nothing().expect("What did you expect?")
        Exception: AssertionError("What did you expect?")
        """
        raise NotImplementedError()

    def is_some(self) -> bool:
        """True if this instance contains a value

        Example
        -------

        >>> Some(2).is_some()
        True
        >>> Nothing().is_some()
        False

        Note
        ----

        It's often easier to use the object's truthiness instead.

        >>> if my_maybe:  # same as if my_maybe.is_some()
        ...     do_things()
        """
        raise NotImplementedError()

    def is_nothing(self) -> bool:
        """True if this instance does not contain a value

        Example
        -------

        >>> Some(2).is_nothing()
        False
        >>> Nothing().is_nothing()
        True

        Note
        ----

        It's often easier to use the object's truthiness instead.

        >>> if not my_maybe:  # same as if my_maybe.is_nothing()
        ...     do_things()

        """
        raise NotImplementedError()

    def map(self, _func: Callable[[T], U]) -> Maybe[U]:
        """Apply a function to the value inside without unwrapping it.

        Example
        -------

        >>> Some("hello").map(str.upper)
        Some("HELLO")
        >>> Nothing().map(abs)
        Nothing()

        """
        raise NotImplementedError()

    @overload
    def filter(self, _func: Callable[[T], TypeGuard[U]]) -> Maybe[U]:
        ...

    @overload
    def filter(self, _func: Callable[[T], Any]) -> Maybe[T]:
        ...

    def filter(self, _func):  # type: ignore[no-untyped-def]
        """Keep the value inside only if it satisfies the given predicate.

        Example
        -------

        >>> Some("9").filter(str.isdigit)
        Some("9")
        >>> Some("foo").filter(str.isdigit)
        Nothing()
        >>> Nothing().filter(str.isdigit)
        Nothing()
        """
        raise NotImplementedError()

    def zip(self, _other: Maybe[U]) -> Maybe[Tuple[T, U]]:
        """Combine two values in a tuple, if both are present.

        Example
        -------

        >>> Some(8).zip(Some(2))
        Some((8, 2))
        >>> Some(7).zip(Nothing())
        Nothing()
        >>> Nothing().zip(Some(3))
        Nothing()
        >>> Nothing().zip(Nothing())
        Nothing()
        """
        raise NotImplementedError()

    def flatmap(self, _func: Callable[[T], Maybe[U]]) -> Maybe[U]:
        """Apply a function (which returns a :class:`~cans.Maybe`)
        to the value inside.
        Then, flatten the result.

        Example
        -------

        >>> def first(s) -> Maybe:
        ...     try:
        ...          return Some(s[0])
        ...     except LookupError:
        ...          return Nothing()
        ...
        >>> Some([9, 4]).flatmap(first)
        Some(9)
        >>> Some([]).flatmap(first)
        Nothing()
        >>> Nothing().flatmap(first)
        Nothing()
        """
        raise NotImplementedError()

    def as_optional(self) -> Optional[T]:
        """Convert the value into an possibly-None value.

        Example
        -------

        >>> Some(6).as_optional()
        6
        >>> Nothing().as_optional()
        None

        """
        raise NotImplementedError()

    def setdefault(self, _v: V) -> Maybe[Union[T, V]]:
        """Set a value if one is not already present.

        Example
        -------

        >>> Some(6).setdefault(7)
        Some(6)
        >>> Nothing().setdefault(3)
        Some(3)

        """
        raise NotImplementedError()

    def and_(self, _other: Maybe[U]) -> Maybe[Union[T, U]]:
        """
        Perform a logical AND operation.
        Returns the first Nothing, or the last of the two values.

        Tip
        ---

        Available as the :meth:`~cans.Maybe.and_` method
        as well as the ``&`` operator.

        Example
        -------

        >>> Some(5) & Some(9)
        Some(9)
        >>> Some(5).and_(Some(9))
        Some(9)
        >>> Some(9) & Nothing()
        Nothing()
        >>> Nothing() & Some(8)
        Nothing()

        """
        raise NotImplementedError()

    __and__ = and_

    def or_(self, _other: Maybe[U]) -> Maybe[Union[T, U]]:
        """Perform a logical OR operation.
        Return the first Some, or the last of the two values.

        Tip
        ---

        Available as the :meth:`~cans.Maybe.or_` method
        as well as the ``|`` operator.

        Example
        -------

        >>> Some(5) | Some(9)
        Some(5)
        >>> Some(5).or_(Some(9))
        Some(5)
        >>> Some(9) | Nothing()
        Some(9)
        >>> Nothing() | Some(8)
        Some(8)
        >>> Nothing() | Nothing()
        Nothing()
        """
        raise NotImplementedError()

    __or__ = or_

    def __iter__(self) -> Iterator[T]:
        """Iterate over the contained item, if present.

        Example
        -------

        >>> list(Some(5))
        [5]
        >>> list(Nothing())
        []
        """
        raise NotImplementedError()

    def __contains__(self, _v: object) -> bool:
        """Check if the item is contained in this object.

        Example
        -------

        >>> 5 in Some(5)
        True
        >>> 4 in Some(8)
        False
        >>> 1 in Nothing()
        False
        """
        raise NotImplementedError()

    def __len__(self) -> int:
        """The number of items contained (0 or 1)

        Example
        -------

        >>> len(Some(5))
        1
        >>> len(Nothing())
        0
        """
        raise NotImplementedError()

    @overload
    def __getitem__(self, _i: int) -> T:
        ...

    @overload
    def __getitem__(self, _i: slice) -> Maybe[T]:
        ...

    def __getitem__(self, _i: Union[int, slice]) -> Union[T, Maybe[T]]:
        """Get the item from this container by index.
        Part of the :class:`~collections.abc.Sequence` API.

        Behaves similarly to a list of one or zero items.

        Example
        -------

        >>> Some(6)[0]
        6
        >>> Some(8)[8]
        Exception: IndexError
        >>> Nothing()[0]
        Exception: IndexError
        ...
        >>> Some(6)[:]
        Some(6)
        >>> Some(2)[:9:4]
        Some(2)
        >>> Some(7)[2:]
        Nothing()
        >>> Nothing()[:]
        Nothing()
        >>> Nothing()[2:9:5]
        Nothing()
        """
        raise NotImplementedError()


@final
@dataclass(frozen=True, repr=False)
class Some(Maybe[T]):
    """The version of :class:`~cans.Maybe` which contains a value.

    Example
    -------

    >>> a: Maybe[int] = Some(-8)
    >>> a.map(abs).unwrap()
    8

    """

    __slots__ = ("_value",)

    _value: T

    def flatten(self: Some[Maybe[U]]) -> Maybe[U]:
        return self._value

    def unwrap(self) -> T:
        return self._value

    def unwrap_or(self, _default: V) -> Union[T, V]:
        return self._value

    def expect(self, _msg: str) -> T:
        return self._value

    def is_some(self) -> bool:
        return True

    def is_nothing(self) -> bool:
        return False

    def map(self, _func: Callable[[T], U]) -> Maybe[U]:
        return Some(_func(self._value))

    @overload
    def filter(self, _func: Callable[[T], TypeGuard[U]]) -> Maybe[U]:
        ...

    @overload
    def filter(self, _func: Callable[[T], Any]) -> Maybe[T]:
        ...

    def filter(self, _func):  # type: ignore[no-untyped-def]
        return self if _func(self._value) else _NOTHING

    def zip(self, _other: Maybe[U]) -> Maybe[Tuple[T, U]]:
        return (
            Some((self._value, _other.unwrap()))
            if _other.is_some()
            else _NOTHING
        )

    def flatmap(self, _func: Callable[[T], Maybe[U]]) -> Maybe[U]:
        return _func(self._value)

    def as_optional(self) -> Optional[T]:
        return self._value

    def setdefault(self, _v: V) -> Maybe[Union[T, V]]:
        return self

    def and_(self, _other: Maybe[U]) -> Maybe[Union[T, U]]:
        return _other

    __and__ = and_

    def or_(self, _other: Maybe[U]) -> Maybe[Union[T, U]]:
        return self

    __or__ = or_

    def __repr__(self) -> str:
        return f"Some({self._value})"

    def __iter__(self) -> Iterator[T]:
        yield self._value

    def __contains__(self, _v: object) -> bool:
        return self._value == _v

    def __len__(self) -> int:
        return 1

    def __bool__(self) -> bool:
        return True

    def __getstate__(self) -> tuple:
        return (self._value,)

    def __setstate__(self, state: tuple) -> None:
        object.__setattr__(self, "_value", state[0])

    @overload
    def __getitem__(self, _i: int) -> T:
        ...

    @overload
    def __getitem__(self, _i: slice) -> Maybe[T]:
        ...

    def __getitem__(self, _i: Union[int, slice]) -> Union[T, Maybe[T]]:
        if isinstance(_i, slice):
            return self if _i.indices(1)[:2] == (0, 1) else _NOTHING
        elif _i == 0:
            return self._value
        else:
            raise IndexError("Only index 0 can be retrieved from container.")


@final
@dataclass(frozen=True)
class Nothing(Maybe[T]):
    """The version of :class:`~cans.Maybe` which does not contain a value.

    Example
    -------

    >>> a: Maybe[int] = Nothing()
    >>> a.map(abs).unwrap_or("nope")
    "nope"

    """

    __slots__ = ()

    def flatten(self: Maybe[Maybe[U]]) -> Maybe[U]:
        return _NOTHING

    def unwrap(self) -> T:
        raise TypeError("Cannot unwrap an empty `Maybe`.")

    def unwrap_or(self, _default: V) -> Union[T, V]:
        return _default

    def expect(self, _msg: str) -> T:
        raise AssertionError(_msg)

    def is_some(self) -> bool:
        return False

    def is_nothing(self) -> bool:
        return True

    def map(self, _func: Callable[[T], U]) -> Maybe[U]:
        return _NOTHING

    @overload
    def filter(self, _func: Callable[[T], TypeGuard[U]]) -> Maybe[U]:
        ...

    @overload
    def filter(self, _func: Callable[[T], Any]) -> Maybe[T]:
        ...

    def filter(self, _func):  # type: ignore[no-untyped-def]
        return _NOTHING

    def zip(self, _other: Maybe[U]) -> Maybe[Tuple[T, U]]:
        return _NOTHING

    def flatmap(self, _func: Callable[[T], Maybe[U]]) -> Maybe[U]:
        return _NOTHING

    def as_optional(self) -> Optional[T]:
        return None

    def setdefault(self, _v: V) -> Maybe[Union[T, V]]:
        return Some(_v)

    def and_(self, _other: Maybe[U]) -> Maybe[Union[T, U]]:
        return _NOTHING

    __and__ = and_

    def or_(self, _other: Maybe[U]) -> Maybe[Union[T, U]]:
        return _other

    __or__ = or_

    def __iter__(self) -> Iterator[T]:
        return _EMPTY_ITERATOR

    def __contains__(self, _v: Any) -> bool:
        return False

    def __len__(self) -> int:
        return 0

    def __bool__(self) -> bool:
        return False

    def __getstate__(self) -> tuple:
        return ()

    def __setstate__(self, state: tuple) -> None:
        pass

    @overload
    def __getitem__(self, _i: int) -> T:
        ...

    @overload
    def __getitem__(self, _i: slice) -> Maybe[T]:
        ...

    def __getitem__(self, _i: Union[int, slice]) -> Union[T, Maybe[T]]:
        if isinstance(_i, slice):
            return _NOTHING
        else:
            raise IndexError("No items in this container.")


_NOTHING: Maybe = Nothing()
_EMPTY_ITERATOR: Iterator = iter(())


class Lazy(Generic[T]):
    """Container for a lazily computed value.
    Useful for implementing lazy loading or I/O behavior.

    >>> Lazy(lambda: input('what is your name?'))
    ...

    Note
    ----
    :class:`~cans.Lazy` instances are mutable by necessity because they
    need to remember whether they've been evaluated.
    Therefore they are not hashable.

    Note
    ----
    If evaluating a :class:`~cans.Lazy` raises an exception,
    this is not cached. A subsequent call will lead to another evaluation.
    """

    __slots__ = ("_evaluator", "_result")

    def __init__(self, __evaluator: Callable[[], T]) -> None:
        self._evaluator = __evaluator
        self._result: Maybe[T] = _NOTHING

    @staticmethod
    def wrap(__value: V) -> Lazy[V]:
        """Wrap a value into a lazy one."""
        v = Lazy(lambda: __value)
        v._result = Some(__value)
        return v

    def flatten(self: Lazy[Lazy[U]]) -> Lazy[U]:
        """Flatten a nested container."""
        return self._result.unwrap_or(Lazy(lambda: self()()))

    def unwrap(self) -> T:
        """Get the contained value, evaluating it if necessary.

        Note
        ----
        You can also call the object itself for the same effect.

        >>> my_lazy()  # same as my_lazy.unwrap()

        """
        return self()

    def __call__(self) -> T:
        """Get the contained value, evaluating it if necessary."""
        if not self._result:
            self._result = Some(self._evaluator())
        return self._result.unwrap()

    def map(self, _func: Callable[[T], U]) -> Lazy[U]:
        """Apply a function to the contained value."""
        return Lazy(lambda: _func(self()))

    def zip(self, _other: Lazy[U]) -> Lazy[Tuple[T, U]]:
        return Lazy(lambda: (self(), _other()))

    def is_evaluated(self) -> bool:
        """Whether the contained expression has been evaluated already."""
        return self._result.is_some()

    def __repr__(self) -> str:
        return f"Lazy({self._result.unwrap_or('?')})"

    def __hash__(self) -> int:
        raise TypeError("Lazy objects cannot be hashed")
