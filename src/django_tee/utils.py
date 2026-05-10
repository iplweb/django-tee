from io import StringIO
from operator import neg


class TeeIO(StringIO):
    """StringIO that ALSO forwards every write to an `original` stream.

    Used to capture stdout/stderr while still letting it land on the
    real terminal — so a cron job's wrapper can persist the output but
    a human running the command interactively still sees it scroll by.

    Only ``write`` is overridden — the inherited ``writelines`` calls
    ``self.write`` per line internally, so it picks up forwarding for
    free. Overriding ``writelines`` separately would duplicate every
    line on the original stream.
    """

    def __init__(self, original, *args, **kw):
        super().__init__(*args, **kw)
        self.original = original

    def write(self, *args, **kw):
        # Capture first (StringIO.write never raises), then forward to
        # the original stream. If forwarding raises (broken terminal,
        # closed pipe), the capture is already done — the audit trail
        # survives even when the user's tty does not.
        result = super().write(*args, **kw)
        self.original.write(*args, **kw)
        return result


def last_n_lines(s, nlines):
    if s is None:
        return None
    lines = s.split("\n")
    prefix = ""
    if len(lines) > nlines:
        prefix = "[...]\n"
    return prefix + "\n".join(lines[neg(nlines) :])
