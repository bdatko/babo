import logging
from pathlib import Path

import click

from babo.logging_setup import LOGLEVEL, LogLevel, setup_logging
from babo.install import install as install_command

logger = logging.getLogger(__name__)


@click.group(no_args_is_help=True)
@click.option(
    "--log-level",
    type=LOGLEVEL,
    default=LogLevel.WARNING,
    help="""Set logging level.""",
    show_default=True,
    required=False,
)
@click.option(
    "--log-file",
    type=click.Path(file_okay=True, dir_okay=False, writable=True, path_type=Path),
    help="""The file to write logs.""",
    required=False,
)
@click.option(
    "--json-logs",
    is_flag=True,
    default=False,
    show_default=True,
    help="""
        When [--LOG-FILE] is used, specify if the logs are formatted as JSON.
        Note, this option does nothing if no [--LOG-FILE] is provided.
        """,
)
@click.version_option(package_name="babo", prog_name="babo")
@click.pass_context
def cli(
    ctx: click.Context, log_level: LogLevel, log_file: Path, *, json_logs: bool = False
) -> None:
    ctx.ensure_object(dict)
    ctx.obj["LOGLEVEL"] = log_level
    setup_logging(log_level=log_level, log_file=log_file, json_logs=json_logs)
    logger.setLevel(ctx.obj["LOGLEVEL"].name)

cli.add_command(install_command)
