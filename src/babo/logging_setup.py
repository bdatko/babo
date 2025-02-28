import atexit
import json
import logging
import logging.config
from datetime import UTC, datetime
from enum import Enum
from importlib import resources
from logging.handlers import QueueHandler, QueueListener
from pathlib import Path
from queue import Queue
from typing import Any, final, override

import click

LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class LogLevel(Enum):
    NOTSET = 0
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class LogLevelParamType(click.ParamType):
    name: str = "loglevel"

    @override
    def convert(
        self, value: Any, param: click.Parameter | None, ctx: click.Context | None
    ) -> LogLevel:
        if isinstance(value, LogLevel):
            return value

        names = [name for name, _ in LogLevel.__members__.items()]

        try:
            match value:
                case str() if value.isnumeric():
                    return LogLevel(int(value))
                case str() if value in names:
                    return LogLevel[value]
                case str() if value.upper() in names:
                    return LogLevel[value.upper()]
                case int():
                    return LogLevel(value)
                case _:
                    return LogLevel(value)
        except ValueError:
            choices = ", ".join(
                [f"{value.name!r} or {value.value}" for value in LogLevel]
            )
            msg = f"{value!r} is not one of {choices}."
            self.fail(msg, param, ctx)


def setup_logging(
    *,
    log_level: LogLevel = LogLevel.WARNING,
    log_file: None | Path = None,
    json_logs: bool = False,
) -> None:
    config_file = resources.files("babo.config").joinpath("config.json")
    with config_file.open(mode="r", encoding="utf-8") as file:
        config: dict[str, Any] = json.load(file)

    config["loggers"]["root"]["level"] = log_level.name

    if log_file:
        del config["handlers"]["stderr"]
        config["loggers"]["root"]["handlers"].remove("stderr")
        config["handlers"]["file_json"]["filename"] = str(log_file)
    else:
        del config["handlers"]["file_json"]
        config["loggers"]["root"]["handlers"].remove("file_json")

    if log_file and json_logs:
        config["handlers"]["file_json"]["formatter"] = "json"

    logging.config.dictConfig(config)
    que: Queue[logging.LogRecord] = Queue(-1)
    queue_handler = QueueHandler(que)
    root = logging.getLogger(name=None)
    handlers = root.handlers[:]
    root.handlers = []
    listener = QueueListener(que, *handlers, respect_handler_level=True)
    root.addHandler(queue_handler)
    listener.start()
    _ = atexit.register(listener.stop)


@final
class JSONFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        fmt_keys: dict[str, str] | None = None,
    ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord):
        always_fields = {
            "message": record.getMessage(),
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message = {
            key: msg_val
            if (msg_val := always_fields.pop(val, None)) is not None
            else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message


class NonErrorFilter(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return record.levelno <= logging.INFO

LOGLEVEL = LogLevelParamType()
