import importlib
import pickle
import sys
from datetime import date, datetime, time
from typing import Collection, Iterable, Union

import pytest

from cans import Maybe, Nothing, Some


def _inverse(n: int) -> Maybe[float]:
    try:
        return Some(1 / n)
    except ZeroDivisionError:
        return Nothing()


def _incr(n: int) -> int:
    return n + 1


def _midnight(d: date) -> datetime:
    return datetime.combine(d, time())


def test_class_structure():
    with pytest.raises(TypeError, match="instantiate"):
        Maybe()

    # check typing
    x: Maybe = Some(5)
    y: Maybe[int] = Nothing()
    z: Collection[str] = Nothing()

    assert issubclass(Some, Iterable)
    assert issubclass(Nothing, Collection)

    del x, y, z


def test_some_basics():
    assert Some(5) == Some(5)
    assert hash(Some(7)) == hash(Some(7))
    assert Some(0).is_some()
    assert not Some(0).is_nothing()
    assert repr(Some(4)) == "Some(4)"
    assert isinstance(Some(2), Maybe)


def test_nothing_basics():
    assert Nothing() == Nothing()
    assert hash(Nothing()) == hash(Nothing())
    assert Nothing().is_nothing()
    assert not Nothing().is_some()
    assert repr(Nothing()) == "Nothing()"


def test_from_optional():
    assert Maybe.from_optional(5) == Some(5)
    assert Maybe.from_optional(0) == Some(0)
    assert Maybe.from_optional(None) == Nothing()


def test_unwrap():
    assert Some(8).unwrap() == 8
    assert Some(0).unwrap() == 0

    with pytest.raises(TypeError, match="empty"):
        Nothing().unwrap()


def test_unwrap_or():
    assert Some(8).unwrap_or(9) == 8
    assert Some(0).unwrap_or(3) == 0
    assert Nothing().unwrap_or(9) == 9

    # check type inference
    _: Union[date, int] = Some(4).unwrap_or(date(2020, 1, 1))


def test_expect():
    assert Some(8).expect("foo") == 8
    assert Some(0).expect("help!") == 0

    with pytest.raises(AssertionError, match="foo"):
        Nothing().expect("foo")


def test_map():
    assert Some(3).map(_incr) == Some(4)
    assert Some(0).map(_incr) == Some(1)
    assert Nothing().map(_incr) == Nothing()

    # contra- and co-variance
    _: Maybe[date] = Some(datetime(2020, 1, 1, 1, 2)).map(_midnight)


def test_flatten():
    assert Some(Some(5)).flatten() == Some(5)
    assert Some(Nothing()).flatten() == Nothing()
    assert Nothing().flatten() == Nothing()


def test_iter():
    assert list(Some(5)) == [5]
    assert list(Some(0)) == [0]
    assert list(Nothing()) == []
    assert list(reversed(Some(5))) == [5]
    assert list(reversed(Some(0))) == [0]
    assert list(reversed(Nothing())) == []


def test_flatmap():
    assert Some(2).flatmap(_inverse) == Some(0.5)
    assert Some(0).flatmap(_inverse) == Nothing()
    assert Nothing().flatmap(_inverse) == Nothing()


def test_contains():
    assert 2 in Some(2)
    assert 4 not in Some(2)
    assert 9 not in Nothing()


def test_len():
    assert len(Some(4)) == 1
    assert len(Nothing()) == 0


def test_bool():
    assert Some(4)
    assert not Nothing()


def test_setdefault():
    assert Some(2).setdefault(9) == Some(2)
    assert Nothing().setdefault(3) == Some(3)

    # check mypy type inference
    _: Maybe[Union[int, date]] = Some(2).setdefault(date(2020, 1, 1))


def test_filter():
    assert Some("5").filter(str.isdigit) == Some("5")
    assert Some("foo").filter(str.isdigit) == Nothing()
    assert Nothing().filter(str.isdigit) == Nothing()


def test_zip():
    assert Some(5).zip(Some(9)) == Some((5, 9))
    assert Some(5).zip(Nothing()) == Nothing()
    assert Nothing().zip(Some(8)) == Nothing()
    assert Nothing().zip(Nothing()) == Nothing()


def test_as_optional():
    assert Some(6).as_optional() == 6
    assert Some(None).as_optional() is None
    assert Nothing().as_optional() is None


def test_and():
    assert Some(2).and_(Some(9)) == Some(9)
    assert Some(8).and_(Nothing()) == Nothing()
    assert Nothing().and_(Nothing()) == Nothing()
    assert Nothing().and_(Some(8)) == Nothing()

    assert Some(5) & Some(9) == Some(9)
    assert Some(5) & Nothing() == Nothing()
    assert Nothing() & Nothing() == Nothing()
    assert Nothing() & Some(8) == Nothing()

    # check mypy type inference
    _: Maybe[Union[int, date]] = Some(2) & Some(date(2020, 1, 1))


def test_or():
    assert Some(2).or_(Some(9)) == Some(2)
    assert Some(8).or_(Nothing()) == Some(8)
    assert Nothing().or_(Nothing()) == Nothing()
    assert Nothing().or_(Some(5)) == Some(5)

    assert Some(5) | Some(9) == Some(5)
    assert Some(5) | Nothing() == Some(5)
    assert Nothing() | Nothing() == Nothing()
    assert Nothing() | Some(4) == Some(4)


def test_getitem():
    assert Some(2)[0] == 2
    with pytest.raises(IndexError):
        assert Some(4)[1]
    with pytest.raises(IndexError):
        assert Nothing()[0]

    with pytest.raises(IndexError):
        assert Nothing()[4]

    assert Some(2)[:4] == Some(2)
    assert Some(4)[0:0] == Nothing()
    assert Some(1)[4:] == Nothing()
    assert Some(9)[4:9] == Nothing()
    assert Some(8)[:9:4] == Some(8)
    assert Some(7)[::3] == Some(7)
    assert Some(6)[:] == Some(6)

    assert Nothing()[:4] == Nothing()
    assert Nothing()[0:0] == Nothing()
    assert Nothing()[4:] == Nothing()
    assert Nothing()[4:9] == Nothing()
    assert Nothing()[:9:4] == Nothing()
    assert Nothing()[::3] == Nothing()
    assert Nothing()[:] == Nothing()

    # check mypy type inferrence
    _: Maybe[int] = Some(8)[:]
    __: int = Some(8)[0]  # noqa


def test_index():
    assert Some(2).index(2) == 0
    with pytest.raises(ValueError):
        Some(4).index(9)

    with pytest.raises(ValueError):
        Nothing().index(9)


def test_count():
    assert Some(5).count(5) == 1
    assert Some(5).count(3) == 0
    assert Nothing().count(6) == 0


def test_pickle():
    assert pickle.loads(pickle.dumps(Some(2))) == Some(2)
    assert pickle.loads(pickle.dumps(Nothing())) == Nothing()


@pytest.mark.skipif(
    sys.version_info < (3, 10), reason="requires Python >=3.10 "
)
def test_pattern_match():
    # this roundabout way of running the test because pattern matching
    # is invalid syntax in older python versions.
    (importlib.import_module("tests.py310_only").test_maybe_pattern_match())
