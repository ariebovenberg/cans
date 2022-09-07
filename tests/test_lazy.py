import pickle
from functools import partial
from typing import Callable

import pytest

from cans import Lazy


def test_unwrap(mocker):
    f = mocker.Mock(return_value=9)
    v = Lazy(f)
    assert not v.is_evaluated()
    assert v.unwrap() == 9
    assert v() == 9
    assert v.is_evaluated()
    assert v.unwrap() == 9
    assert v.is_evaluated()
    assert f.call_count == 1

    assert Lazy.wrap(8).unwrap() == 8

    # typechecks
    _: Callable[[], str] = Lazy.wrap("foo")


def test_pickle():
    v = Lazy(partial(int, "  4"))
    assert pickle.loads(pickle.dumps(v))() == 4


def test_map(mocker):
    f = mocker.Mock(return_value=-9)
    v = Lazy(f)
    assert v.map(abs)() == 9
    assert v() == -9
    f2 = mocker.Mock(side_effect=lambda x: x + 1)
    v2 = v.map(f2)
    assert v2() == -8
    assert v2() == -8
    assert f2.call_count == 1
    assert f.call_count == 1


def test_zip(mocker):
    f1 = mocker.Mock(return_value=9)
    f2 = mocker.Mock(return_value=3)
    v1 = Lazy(f1)
    v2 = Lazy(f2)
    v2()
    zipped = v1.zip(v2)
    assert f1.call_count == 0
    assert f2.call_count == 1
    assert zipped.unwrap() == (9, 3)
    assert f1.call_count == 1
    assert f2.call_count == 1


def test_repr():
    v = Lazy(lambda: 3)
    assert repr(v) == "Lazy(?)"
    v.unwrap()
    assert repr(v) == "Lazy(3)"


def test_hash():
    with pytest.raises(TypeError, match="hash"):
        hash(Lazy.wrap(4))


def test_flatten_partially_evaluated(mocker):
    a_func = mocker.Mock(return_value="foo")
    a = Lazy(a_func)
    b_func = mocker.Mock(return_value=a)
    b = Lazy(b_func)
    c = b.flatten()
    assert a_func.call_count == 0
    assert b_func.call_count == 0

    a()
    assert a_func.call_count == 1

    assert c.map(len)() == 3
    assert a_func.call_count == 1
    assert b_func.call_count == 1
    assert a.is_evaluated()
    assert b.is_evaluated()
    assert c.is_evaluated()

    assert c.map(str.title)() == "Foo"
    assert a_func.call_count == 1
    assert b_func.call_count == 1


def test_flatten_nothing_evaluated(mocker):
    a_func = mocker.Mock(return_value="foo")
    a = Lazy(a_func)
    b_func = mocker.Mock(return_value=a)
    b = Lazy(b_func)
    c = b.flatten()
    assert a_func.call_count == 0
    assert b_func.call_count == 0
    assert not c.is_evaluated()

    assert c.map(len)() == 3
    assert a_func.call_count == 1
    assert b_func.call_count == 1
    assert a.is_evaluated()
    assert b.is_evaluated()
    assert c.is_evaluated()
