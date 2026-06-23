import logging
from log import logger

def test_logger_name():
    # logger should be named "ingest"
    assert logger.name == "ingest"

def test_logger_level():
    # logger should be set to INFO level
    assert logger.level == logging.INFO

def test_logger_has_handler():
    # logger should have at least one handler attached
    assert len(logger.handlers) > 0

def test_logger_handler_is_stream():
    # the handler should be a StreamHandler (console output)
    assert isinstance(logger.handlers[0], logging.StreamHandler)
