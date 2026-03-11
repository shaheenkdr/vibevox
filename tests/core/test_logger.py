import logging
import os
from unittest.mock import patch


def test_logger_default_level_is_warning():
    # Remove any cached logger to get a fresh one
    logging.root.manager.loggerDict.pop("vibevox.test_default", None)
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("VIBEVOX_LOG_LEVEL", None)
        from vibevox.core.logger import get_logger
        log = get_logger("vibevox.test_default")
    assert log.level == logging.WARNING


def test_logger_respects_env_var():
    logging.root.manager.loggerDict.pop("vibevox.test_env", None)
    with patch.dict(os.environ, {"VIBEVOX_LOG_LEVEL": "DEBUG"}):
        from vibevox.core.logger import get_logger
        log = get_logger("vibevox.test_env")
    assert log.level == logging.DEBUG


def test_logger_invalid_level_falls_back_to_warning():
    logging.root.manager.loggerDict.pop("vibevox.test_invalid", None)
    with patch.dict(os.environ, {"VIBEVOX_LOG_LEVEL": "NONSENSE"}):
        from vibevox.core.logger import get_logger
        log = get_logger("vibevox.test_invalid")
    assert log.level == logging.WARNING


def test_configure_logging_updates_existing_loggers():
    from vibevox.core.logger import get_logger, configure_logging
    logging.root.manager.loggerDict.pop("vibevox.test_configure", None)
    log = get_logger("vibevox.test_configure")
    assert log.level == logging.WARNING
    configure_logging("DEBUG")
    assert log.level == logging.DEBUG
    # restore so other tests are not affected
    configure_logging("WARNING")
