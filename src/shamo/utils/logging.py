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
            _log_with_pattern(line, self.logger, self.log_level, self.pattern)

    def flush(self):
        """A dummy flush function."""
        pass


def _log_with_pattern(line, logger, log_level, pattern):
    """Log a text and check a pattern.

    Parameters
    ----------
    line : str
        The line to log.
    logger : logging.Logger
        The logger.
    log_level : int
        The logging level.
    pattern : str
        A pattern containing a 'level' and a 'text' group.
    """
    line = line.strip()
    lines = line.split("\r")
    for line in lines:
        match = None
        if pattern != "":
            match = re.search(pattern, line)
        if match is not None:
            if match.group("level"):
                logger.log(log_level, match.group("text"))
            else:
                logger.log(
                    log_level,
                    f"{match.group('text').strip()} ({match.group('percentage')})",
                )
        else:
            if line.strip() != "":
                logger.log(log_level, line)


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


def subprocess_to_logger(process, logger=None, log_level=logging.INFO, pattern=""):
    """A context manager to pipe the output of a subprocess to the logger.

    Parameters
    ----------
    logger : logging.Logger
        The logger to pipe the stream to.
    log_level : int
        The logging level of the piped messages.
    pattern : str
        A pattern containing a 'level' and a 'text' group.
    """
    with process.stdout as pipe:
        with stream_to_logger(logger, log_level, pattern):
            for line in iter(pipe.readline, b""):
                _log_with_pattern(line.decode("utf-8"), logger, log_level, pattern)
    return process.wait()
