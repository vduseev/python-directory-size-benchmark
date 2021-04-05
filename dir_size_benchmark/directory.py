from logging import log
import os
from pathlib import Path

from loguru import logger
import loguru


class DirectoryAlreadyExists(Exception):
    pass


class Directory:
    def __init__(self, config) -> None:
        self.config = config
        self.path = Path(config.path)

    def create(self):

        self._assert_dir_does_not_exist()

        logger.info(f"Initializing benchmark directory at {self.path}")
        self._create(self.path, 0)
        logger.info(f"Benchmark directory initialized!")

    def _create(self, path, level):

        self.path.mkdir()

        for file_idx in range(self.config.file_count):

            filename = path / f"file{file_idx:03}.txt"
            with open(filename, "wb") as f:
                f.write(b"foo")

        if level > self.config.recurse:
            return

        for dir_idx in range(self.config.dir_count):

            dirname = path / f"dir{dir_idx:03}"
            self._create(dirname, level + 1)

    def _assert_dir_does_not_exist(self):
        if self.path.is_dir() and self.path.exists():
            logger.error(f"Directory {self.path} already exists")
            raise DirectoryAlreadyExists(f"{self.path}")
