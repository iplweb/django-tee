"""Tests for django_tee.utils — pure-Python helpers, no DB needed."""

from io import StringIO

from django_tee.utils import TeeIO, last_n_lines


def test_tee_io_forwards_writes_to_original():
    original = StringIO()
    tee = TeeIO(original)

    tee.write("hello\n")
    tee.write("world\n")

    assert original.getvalue() == "hello\nworld\n"
    assert tee.getvalue() == "hello\nworld\n"


def test_tee_io_writelines_forwards_to_original():
    original = StringIO()
    tee = TeeIO(original)

    tee.writelines(["a\n", "b\n", "c\n"])

    assert original.getvalue() == "a\nb\nc\n"
    assert tee.getvalue() == "a\nb\nc\n"


def test_tee_io_still_captures_when_original_raises():
    """Original stream errors must NOT prevent capture — that's the whole
    point of having both streams: a flaky terminal shouldn't kill the
    audit trail."""

    class BrokenStream:
        def write(self, *args, **kwargs):
            raise OSError("stream is broken")

        def writelines(self, *args, **kwargs):
            raise OSError("stream is broken")

    tee = TeeIO(BrokenStream())

    try:
        tee.write("captured\n")
    except OSError:
        pass

    # The capture happened in the `finally` branch, so the value lives
    # on even though the forwarded write blew up.
    assert tee.getvalue() == "captured\n"


def test_last_n_lines_none_returns_none():
    assert last_n_lines(None, nlines=5) is None


def test_last_n_lines_short_string_returned_as_is():
    s = "a\nb\nc"
    assert last_n_lines(s, nlines=5) == "a\nb\nc"


def test_last_n_lines_truncates_with_marker():
    s = "1\n2\n3\n4\n5\n6\n7"
    assert last_n_lines(s, nlines=3) == "[...]\n5\n6\n7"
