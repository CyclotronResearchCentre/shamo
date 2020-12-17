"""API for `shamo.utils.logging`."""
from contextlib import contextmanager
import logging
import re
import sys

from wurlitzer import sys_pipes


class StreamToLogger(object):
    """Pipe a stream to a logger.

    The implementation is based on the blog post available at:
    http://techies-world.com/how-to-redirect-stdout-and-stderr-to-a-logger-in-python/

    Parameters
    ----------
    logger : logging.Logger
        The logger to pipe the stream to.
    log_level : int
        The logging level of the piped messages.
    pattern : str
        A pattern containing a 'level' and a 'text' group.
    """

    pattern = re.compile("^(?P<level>[\w]*) +: (?P<text>.*)$")

    def __init__(self, logger, log_level=logging.INFO, pattern=""):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ""
        self.pattern = re.compile(pattern)

    def write(self, buf):
        """Write a message to the logger.

        Parameters
        ----------
        buf : bytes
            The buffer to read from.
        """
        for line in buf.rstrip().splitlines():
            line = line.rstrip()
            match = None
            if self.pattern != "":
                match = re.search(self.pattern, line)
            if match is not None:
                self.logger.log(self.log_level, match.group("text"))
            else:
                self.logger.log(self.log_level, line)

    def flush(self):
        """A dummy flush function."""
        pass


@contextmanager
def stream_to_logger(logger=None, log_level=logging.INFO, pattern=""):
    """A context manager where everything pushed to stdout is piped to the logger.

    Parameters
    ----------
    logger : logging.Logger
        The logger to pipe the stream to.
    log_level : int
        The logging level of the piped messages.
    pattern : str
        A pattern containing a 'level' and a 'text' group.
    """
    logger = logging.getLogger(__name__) if logger is None else logger
    stream = StreamToLogger(logger, log_level, pattern)
    tmp = sys.stdout
    sys.stdout = stream
    with sys_pipes():
        try:
            yield
        finally:
            sys.stdout = tmp
