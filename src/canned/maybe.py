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
    Union,
    overload,
)

from .common import T, T_co, U, U_co


def of(__v: T) -> Maybe[T]:
    """Create a maybe container of the given value.

    Note: even `None` will be wrapped in a container.
            Use `from_optional` if you need special behavior for `None`.
    """
    return Just(__v)


def from_optional(__v: Optional[T_co]) -> Maybe[T_co]:
    """Create a maybe container from the given value, which may be `None`.
    In that case, it'll be an empty Maybe.
    """
    return _NOTHING if __v is None else Just(__v)


def flatten(m: Maybe[Maybe[T_co]]) -> Maybe[T_co]:
    """Flatten two nested maybes."""
    return m.unwrap() if m.is_just() else m  # type: ignore


# Why not the Rust-like Option(Some/None) terminology?
#     (1) it's confusing with Optional
#     (2) `None` is reserved in Python
class Maybe(Generic[T_co], Sequence[T_co]):
    __slots__ = ()

    def __init__(self) -> None:
        raise TypeError(
            "Can't instantiate Maybe directly. "
            "Use the factory methods `of` and `from_optional` instead."
        )

    def unwrap(self) -> T_co:
        """Unwrap the value in this container.
        If there is no value, `TypeError` is raised.
        """
        raise NotImplementedError()

    def unwrap_or(self, default: U) -> Union[T_co, U]:
        """Unwrap the value in this container.
        If there is no value, return the given default.
        """
        raise NotImplementedError()

    def expect(self, msg: str) -> T_co:
        """Unwrap the value in this container.
        If there is no value, raise an AssertionError with message
        """
        raise NotImplementedError()

    def is_just(self) -> bool:
        "True if this `Maybe` contains a value"
        raise NotImplementedError()

    def is_nothing(self) -> bool:
        "True if this `Maybe` does not contain a value"
        raise NotImplementedError()

    def map(self, __f: Callable[[T_co], U_co]) -> Maybe[U_co]:
        """Apply a function to the value inside the `Maybe`,
        without unwrapping it.
        """
        raise NotImplementedError()

    def filter(self, __f: Callable[[T_co], bool]) -> Maybe[T_co]:
        "Keep the value inside only if it satisfies the given predicate."
        raise NotImplementedError()

    def zip(self, other: Maybe[U_co]) -> Maybe[Tuple[T_co, U_co]]:
        "Combine two values in a tuple, if both are present."
        raise NotImplementedError()

    def flatmap(self, __f: Callable[[T_co], Maybe[U_co]]) -> Maybe[U_co]:
        """Apply a function (which returns a maybe)
        to the value inside the `Maybe`.
        Then, flatten the result.
        """
        raise NotImplementedError()

    def as_optional(self) -> Optional[T_co]:
        "Convert the value into an possibly-None value."
        raise NotImplementedError()

    def setdefault(self, v: U) -> Maybe[Union[T_co, U]]:
        """Set a value if one is not already present."""
        raise NotImplementedError()

    def and_(self, other: Maybe[U_co]) -> Maybe[Union[T_co, U_co]]:
        """Perform a logical AND operation.
        Return the first Nothing(), or the last of the two values.
        """
        raise NotImplementedError()

    __and__ = and_

    def or_(self, other: Maybe[U_co]) -> Maybe[Union[T_co, U_co]]:
        """Perform a logical OR operation.
        Return the first Just, or the last of the two values.
        """
        raise NotImplementedError()

    __or__ = or_

    def __iter__(self) -> Iterator[T_co]:
        raise NotImplementedError()

    def __contains__(self: Maybe[T], v: object) -> bool:
        raise NotImplementedError()

    def __len__(self) -> int:
        raise NotImplementedError()

    @overload
    def __getitem__(self, __i: int) -> T_co:
        ...

    @overload
    def __getitem__(self, __i: slice) -> Maybe[T_co]:
        ...

    def __getitem__(self, __i: Union[int, slice]) -> Union[T_co, Maybe[T_co]]:
        """Get the item from this container by index.
        Part of the `Sequence` API."""
        raise NotImplementedError()


@dataclass(frozen=True, repr=False)
class Just(Maybe[T_co]):
    __slots__ = "_value"

    _value: T_co

    def unwrap(self) -> T_co:
        return self._value

    def unwrap_or(self, default: U) -> Union[T_co, U]:
        return self._value

    def expect(self, msg: str) -> T_co:
        return self._value

    def is_just(self) -> bool:
        return True

    def is_nothing(self) -> bool:
        return False

    def map(self, __f: Callable[[T_co], U_co]) -> Maybe[U_co]:
        return Just(__f(self._value))

    def filter(self, __f: Callable[[T_co], bool]) -> Maybe[T_co]:
        return self if __f(self._value) else _NOTHING

    def zip(self, other: Maybe[U_co]) -> Maybe[Tuple[T_co, U_co]]:
        return (
            Just((self._value, other.unwrap()))
            if other.is_just()
            else _NOTHING
        )

    def flatmap(self, __f: Callable[[T_co], Maybe[U_co]]) -> Maybe[U_co]:
        return flatten(self.map(__f))

    def as_optional(self) -> Optional[T_co]:
        return self._value

    def setdefault(self, v: U) -> Maybe[Union[T_co, U]]:
        return self

    def and_(self, other: Maybe[U_co]) -> Maybe[Union[T_co, U_co]]:
        return other

    __and__ = and_

    def or_(self, other: Maybe[U_co]) -> Maybe[Union[T_co, U_co]]:
        return self

    __or__ = or_

    def __repr__(self) -> str:
        return f"Just({self._value})"

    def __iter__(self) -> Iterator[T_co]:
        yield self._value

    def __contains__(self: Just[T], v: object) -> bool:
        return self._value == v

    def __len__(self) -> int:
        return 1

    def __bool__(self) -> bool:
        return True

    def __getstate__(self) -> tuple:
        return (self._value,)

    def __setstate__(self, state: tuple) -> None:
        object.__setattr__(self, "_value", state[0])

    @overload
    def __getitem__(self, __i: int) -> T_co:
        ...

    @overload
    def __getitem__(self, __i: slice) -> Maybe[T_co]:
        ...

    def __getitem__(self, __i: Union[int, slice]) -> Union[T_co, Maybe[T_co]]:
        if isinstance(__i, slice):
            return self if __i.indices(1)[:2] == (0, 1) else _NOTHING
        elif __i == 0:
            return self._value
        else:
            raise IndexError("Only index 0 can be retrieved from container.")


@dataclass(frozen=True)
class Nothing(Maybe[T_co]):
    __slots__ = ()

    def unwrap(self) -> T_co:
        raise TypeError("Cannot unwrap an empty `Maybe`.")

    def unwrap_or(self, default: U) -> Union[T_co, U]:
        return default

    def expect(self, msg: str) -> T_co:
        raise AssertionError(msg)

    def is_just(self) -> bool:
        return False

    def is_nothing(self) -> bool:
        return True

    def map(self, __f: Callable[[T_co], U_co]) -> Maybe[U_co]:
        return _NOTHING

    def filter(self, __f: Callable[[T_co], bool]) -> Maybe[T_co]:
        return _NOTHING

    def zip(self, other: Maybe[U_co]) -> Maybe[Tuple[T_co, U_co]]:
        return _NOTHING

    def flatmap(self, __f: Callable[[T_co], Maybe[U_co]]) -> Maybe[U_co]:
        return _NOTHING

    def as_optional(self) -> Optional[T_co]:
        return None

    def setdefault(self, v: U) -> Maybe[Union[T_co, U]]:
        return Just(v)

    def and_(self, other: Maybe[U_co]) -> Maybe[Union[T_co, U_co]]:
        return _NOTHING

    __and__ = and_

    def or_(self, other: Maybe[U_co]) -> Maybe[Union[T_co, U_co]]:
        return other

    __or__ = or_

    def __iter__(self) -> Iterator[T_co]:
        return _EMPTY_ITERATOR

    def __contains__(self: Nothing[Any], v: Any) -> bool:
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
    def __getitem__(self, __i: int) -> T_co:
        ...

    @overload
    def __getitem__(self, __i: slice) -> Maybe[T_co]:
        ...

    def __getitem__(self, __i: Union[int, slice]) -> Union[T_co, Maybe[T_co]]:
        if isinstance(__i, slice):
            return _NOTHING
        else:
            raise IndexError("No items in this container.")


_NOTHING: Maybe = Nothing()
_EMPTY_ITERATOR: Iterator = iter(())
