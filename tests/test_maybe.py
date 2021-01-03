from dataclasses import is_dataclass
from datetime import date, datetime, time
from typing import Iterable, Union, Collection

import pytest

from dango import maybe
from dango.maybe import Just, Maybe, Nothing


def _inverse(n: int) -> Maybe[float]:
    try:
        return Just(1 / n)
    except ZeroDivisionError:
        return Nothing()


def _incr(n: int) -> int:
    return n + 1


def _midnight(d: date) -> datetime:
    return datetime.combine(d, time())


def test_class_structure():
    with pytest.raises(TypeError, match="instantiate"):
        maybe.Maybe()
    assert isinstance(Just(5), maybe.Maybe)
    assert isinstance(maybe.Nothing(), maybe.Maybe)
    assert issubclass(maybe.Maybe, Iterable)
    assert issubclass(maybe.Maybe, Collection)


def test_just_basics():
    assert is_dataclass(Just(2))
    assert Just(5) == Just(5)
    assert hash(Just(7)) == hash(Just(7))
    assert Just(0).is_just()
    assert not Just(0).is_nothing()
    assert repr(Just(4)) == "Just(4)"


def test_nothing_basics():
    assert is_dataclass(maybe.Nothing())
    assert maybe.Nothing() == maybe.Nothing()
    assert hash(maybe.Nothing()) == hash(maybe.Nothing())
    assert maybe.Nothing().is_nothing()
    assert not maybe.Nothing().is_just()
    assert repr(Nothing()) == "Nothing()"


def test_of():
    assert maybe.of(5) == Just(5)
    assert maybe.of(None) == Just(None)


def test_from_optional():
    assert maybe.from_optional(5) == Just(5)
    assert maybe.from_optional(0) == Just(0)
    assert maybe.from_optional(None) == maybe.Nothing()


def test_unwrap():
    assert Just(8).unwrap() == 8
    assert Just(0).unwrap() == 0

    with pytest.raises(TypeError, match="empty"):
        maybe.Nothing().unwrap()


def test_unwrap_or():
    assert Just(8).unwrap_or(9) == 8
    assert Just(0).unwrap_or(3) == 0
    Nothing().unwrap_or(9) == 9

    # correct handling of types
    k: Union[date, int] = Just(4).unwrap_or(date(2020, 1, 1))
    assert k == 4


def test_expect():
    assert Just(8).expect("foo") == 8
    assert Just(0).expect("help!") == 0

    with pytest.raises(AssertionError, match="foo"):
        maybe.Nothing().expect("foo")


def test_map():
    assert Just(3).map(_incr) == Just(4)
    assert Just(0).map(_incr) == Just(1)
    assert maybe.Nothing().map(_incr) == maybe.Nothing()

    # contra- and co-variance
    _: Maybe[date] = maybe.of(datetime(2020, 1, 1, 1, 2)).map(_midnight)


def test_flatten():
    assert maybe.flatten(Just(Just(5))) == Just(5)
    assert maybe.flatten(Just(Nothing())) == Nothing()
    assert maybe.flatten(Nothing()) == Nothing()


def test_iter():
    assert list(Just(5)) == [5]
    assert list(Just(0)) == [0]
    assert list(Nothing()) == []


def test_flatmap():
    assert Just(2).flatmap(_inverse) == Just(0.5)
    assert Just(0).flatmap(_inverse) == Nothing()
    assert Nothing().flatmap(_inverse) == Nothing()


def test_contains():
    assert 2 in Just(2)
    assert 4 not in Just(2)
    assert 9 not in Nothing()


def test_len():
    assert len(Just(4)) == 1
    assert len(Nothing()) == 0


def test_bool():
    assert Just(4)
    assert not Nothing()


def test_setdefault():
    assert Just(2).setdefault(9) == Just(2)
    assert Nothing().setdefault(3) == Just(3)

    _: Maybe[Union[int, date]] = Just(2).setdefault(date(2020, 1, 1))


def test_filter():
    assert Just("5").filter(str.isdigit) == Just("5")
    assert Just("foo").filter(str.isdigit) == Nothing()
    assert Nothing().filter(str.isdigit) == Nothing()


def test_zip():
    assert Just(5).zip(Just(9)) == Just((5, 9))
    assert Just(5).zip(Nothing()) == Nothing()
    assert Nothing().zip(Just(8)) == Nothing()
    assert Nothing().zip(Nothing()) == Nothing()


def test_as_optional():
    assert Just(6).as_optional() == 6
    assert Just(None).as_optional() is None
    assert Nothing().as_optional() is None


def test_and():
    assert Just(2).and_(Just(9)) == Just(9)
    assert Just(8).and_(Nothing()) == Nothing()
    assert Nothing().and_(Nothing()) == Nothing()
    assert Nothing().and_(Just(8)) == Nothing()

    assert Just(5) & Just(9) == Just(9)
    assert Just(5) & Nothing() == Nothing()
    assert Nothing() & Nothing() == Nothing()
    assert Nothing() & Just(8) == Nothing()

    _: Maybe[Union[int, date]] = Just(2) & Just(date(2020, 1, 1))


def test_or():
    assert Just(2).or_(Just(9)) == Just(2)
    assert Just(8).or_(Nothing()) == Just(8)
    assert Nothing().or_(Nothing()) == Nothing()
    assert Nothing().or_(Just(5)) == Just(5)

    assert Just(5) | Just(9) == Just(5)
    assert Just(5) | Nothing() == Just(5)
    assert Nothing() | Nothing() == Nothing()
    assert Nothing() | Just(4) == Just(4)
