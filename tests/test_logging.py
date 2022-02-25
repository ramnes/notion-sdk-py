import logging

from notion_client.logging import make_console_logger


def test_make_console_logger(caplog):
    logger = make_console_logger()

    with caplog.at_level(logging.INFO, logger="notion_client"):
        logger.info("TEST_LOGGER_INFO_MESSAGE")
        assert caplog.records[0].message == "TEST_LOGGER_INFO_MESSAGE"
        caplog.clear()

    with caplog.at_level(logging.DEBUG, logger="notion_client"):
        logger.debug("TEST_LOGGER_DEBUG_MESSAGE")
        assert caplog.records[0].message == "TEST_LOGGER_DEBUG_MESSAGE"
        caplog.clear()
