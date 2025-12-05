import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class Logger:
    def __init__(self, log_path: Path | None = None, debug: bool = False):
        self.log_path = log_path
        if self.log_path and not self.log_path.exists():
            self.log_path.mkdir(parents=True, exist_ok=True)
        self.debug = debug

    def _formatter(self) -> logging.Formatter:
        format = (
            "[%(asctime)s] "
            "%(levelname)-8s "
            "%(name)s:%(funcName)s:%(lineno)d "
            "- %(message)s"
        )
        return logging.Formatter(
            format,
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    def setup_logger(self, name: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
        logger.propagate = False

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self._formatter())
        logger.addHandler(console_handler)

        # File Handler
        if not self.log_path:
            raise ValueError("log_path is required")
        file_handler = TimedRotatingFileHandler(self.log_path / f"{name}.log", when="D", interval=30, backupCount=12)
        file_handler.setFormatter(self._formatter())
        logger.addHandler(file_handler)

        return logger

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        return logging.getLogger(name)
