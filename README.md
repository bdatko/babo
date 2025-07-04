# babo 바보

A small Python based installation runner to help manage installing software.

```bash
$ babo --help
Usage: babo [OPTIONS] COMMAND [ARGS]...

Options:
  --log-level LOGLEVEL  Set logging level.  [default: LogLevel.WARNING]
  --log-file FILE       The file to write logs.
  --json-logs           When [--LOG-FILE] is used, specify if the logs are
                        formatted as JSON. Note, this option does nothing if
                        no [--LOG-FILE] is provided.
  --version             Show the version and exit.
  --help                Show this message and exit.

Commands:
  install  Install packages for dev-env
```

# How I intend to use this...

0. Install `homebrew` using the `install` script within [`.dotfiles`](https://github.com/bdatko/.dotfiles)
1. Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
2. Use `uv` to install this repo as tool using:
```
uv tool install git+https://github.com/bdatko/babo.git
```
3. `git clone https://github.com/bdatko/.dotfiles`
4. Use `stow` to stow dotfiles. You might have to remove `~/.zshrc` that `uv` added.
5. Use `babo` to install software using:
```
babo install --target-dir ~/.local/share/install-scripts/
```
