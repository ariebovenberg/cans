import pytest

from cans import Lazy, flatten


def test_unwrap(mocker):
    f = mocker.Mock(return_value=9)
    v = Lazy(f)
    assert not v.is_evaluated()
    assert v.unwrap() == 9
    assert v.is_evaluated()
    assert v.unwrap() == 9
    assert v.is_evaluated()
    assert f.call_count == 1

    assert Lazy.wrap(8).unwrap() == 8


def test_map(mocker):
    f = mocker.Mock(return_value=-9)
    v = Lazy(f)
    assert v.map(abs).unwrap() == 9
    assert v.unwrap() == -9
    f2 = mocker.Mock(side_effect=lambda x: x + 1)
    v2 = v.map(f2)
    assert v2.unwrap() == -8
    assert v2.unwrap() == -8
    assert f2.call_count == 1
    assert f.call_count == 1


def test_zip(mocker):
    f1 = mocker.Mock(return_value=9)
    f2 = mocker.Mock(return_value=3)
    v1 = Lazy(f1)
    v2 = Lazy(f2)
    v2.unwrap()
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


def test_flatten():
    v = Lazy(lambda: Lazy(lambda: 8))
    assert v.unwrap().unwrap() == 8
    assert flatten(v).unwrap() == 8

    v2 = Lazy.wrap(Lazy(lambda: 9))
    v2.unwrap() == 9
