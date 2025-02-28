import logging
import os
import sys
from pathlib import Path
from traceback import TracebackException

import click
from plumbum import local
from plumbum.cmd import echo, grep
from plumbum.commands import ProcessExecutionError

logger = logging.getLogger("babo.cli")


def filter_out(file: Path, *, pick: str | None) -> bool:
    check = False
    if pick is not None:
        chain = echo[file.stem] | grep[pick]
        try:
            check, *_ = chain.run(retcode=(0, 1))
            check = bool(check)
        except ProcessExecutionError as exc:
            error = TracebackException.from_exception(exc)
            msg = f"Something went wrong within 'grep' on file: {file.name}\n"
            msg += str(error)
            logger.error(msg)
            raise click.Abort() from exc
    return check


def log(msg: str, *, dry_run: bool) -> None:
    if dry_run:
        msg = f"[DRY_RUN]: {msg}"
        click.echo(msg)
    else:
        click.echo(msg)


def execute(script: Path, *, dry_run: bool) -> None:
    log(f"execute: {script}", dry_run=dry_run)
    if dry_run:
        return
    local[script](stdout=sys.stdout, stderr=sys.stderr)


@click.command(short_help="Install packages for dev-env")
@click.argument("pick", type=click.STRING, default=None, required=False)
@click.option(
    "--target-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=True,
    envvar="BABO_TARGET_DIR",
    help="""
    Specify the target direoctry contain a executables to install.
    """,
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    show_default=True,
    help="""
    Flag to mock all installation only showing the commands to be run.
    """,
)
@click.pass_context
def install(
    ctx: click.Context, pick: str | None, target_dir: Path, *, dry_run: bool = False
):
    """
    Run all installation scripts within a given directory.

    [PICK] is a simple filter to run scripts only matching [PICK]
    """
    msg = f"{pick=!s} | {target_dir=!s} | {dry_run=!s}"
    logger.debug(msg)

    for file in target_dir.iterdir():
        if not (file.is_file() and os.access(file, os.X_OK)):
            continue
        if filter_out(file, pick=pick):
            log(f"filtered: {pick} -- {file.name}", dry_run=dry_run)
            continue

        execute(file, dry_run=dry_run)
