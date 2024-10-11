import logging


# создаем форматтер для отладочных сообщений
_log_format: str = (
    '%(asctime)s - [%(levelname)s] - %(name)s - '
    '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s')


def get_file_handler() -> logging.Handler:
    """Creates a file handler that logs warning messages and higher."""
    handler = logging.FileHandler(
        'errors.log', encoding='utf-8', delay=True, mode='a'
    )
    handler.setLevel(logging.WARNING)
    handler.setFormatter(logging.Formatter(_log_format))
    return handler


def get_stream_handler() -> logging.Handler:
    """Creates a stream handler that logs info messages and higher."""
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    return handler


def get_logger(name: str) -> logging.Logger:
    """Create logger and add configured handlers to logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.handlers = [
        get_file_handler(),
        get_stream_handler()
    ]
    return logger


