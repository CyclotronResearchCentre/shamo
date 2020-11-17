"""Bump version and updates every file that needs to be."""
from datetime import date
import logging
import subprocess as sub
import sys

logger = logging.getLogger(__name__)


def post_process():
    logger.info("POST PROCESSING")

    with open("CHANGELOG.md", "r") as f:
        content = f.readlines()

    logger.info("Adding date in CHANGELOG.md")
    today = date.today()
    content[4] = content[4].strip() + f" - {today.strftime('%y-%m-%d')}\n"

    logger.info("Adding unreleased tag in CHANGELOG.md")
    content.insert(4, "## [Unreleased]\n")
    content.insert(5, "\n")
    with open("CHANGELOG.md", "w") as f:
        f.writelines(content)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    logger.info("BUMPING VERSION")
    cmd = ["bump2version", "--allow-dirty", *sys.argv[1:]]
    sub.run(cmd)
    post_process()
