import logging

import pytest

from src.utils.logger import Logger


class TestSetupLogger:
    def test_creates_logger_with_given_name(self, tmp_path):
        result = Logger(tmp_path / "test.log").setup_logger("my_logger")
        assert result.name == "my_logger"

    def test_debug_mode_sets_debug_level(self, tmp_path):
        result = Logger(tmp_path / "test.log", debug=True).setup_logger("dbg_logger")
        assert result.level == logging.DEBUG

    def test_non_debug_mode_sets_info_level(self, tmp_path):
        result = Logger(tmp_path / "test.log", debug=False).setup_logger("info_logger")
        assert result.level == logging.INFO

    def test_adds_exactly_two_handlers(self, tmp_path):
        result = Logger(tmp_path / "test.log").setup_logger("two_handlers_logger")
        assert len(result.handlers) == 2

    def test_propagate_is_disabled(self, tmp_path):
        result = Logger(tmp_path / "test.log").setup_logger("no_propagate_logger")
        assert result.propagate is False

    def test_creates_log_file_on_first_write(self, tmp_path):
        log_file = tmp_path / "test.log"
        logger = Logger(log_file).setup_logger("file_write_logger")
        logger.info("test message")
        assert log_file.exists()

    def test_default_debug_is_false(self, tmp_path):
        l = Logger(tmp_path / "test.log")
        assert l.debug is False


class TestGetLogger:
    def test_returns_same_instance_as_setup(self, tmp_path):
        created = Logger(tmp_path / "test.log").setup_logger("same_instance_logger")
        retrieved = Logger.get_logger("same_instance_logger")
        assert created is retrieved

    def test_returns_logging_logger_type(self):
        result = Logger.get_logger("any_logger")
        assert isinstance(result, logging.Logger)


class TestFormatter:
    def test_returns_logging_formatter_instance(self, tmp_path):
        formatter = Logger(tmp_path / "test.log")._formatter()
        assert isinstance(formatter, logging.Formatter)
