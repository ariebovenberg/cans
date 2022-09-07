"""Module containing python3.10-only syntax.

A separate module is needed so its import can be skipped completely
in older python versions.
"""
import pytest

from cans import Maybe, Nothing, Some


def _myfunc(m):
    match m:
        case Some(n):
            return str(n)
        case Nothing():
            return 'Nothing!'
        case _:
            return 'what?'


def test_maybe_pattern_match():
    assert _myfunc(Some(5)) == '5'
    assert _myfunc(Nothing()) == 'Nothing!'
    assert _myfunc(5) == 'what?'
