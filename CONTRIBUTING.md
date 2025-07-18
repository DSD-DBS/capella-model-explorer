<!--
 ~ Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Contributing

Thanks for your interest in our project. Contributions are always welcome!

We are committed to fostering a welcoming, respectful, and harassment-free
environment. Be kind!

If you have questions, ideas or want to report a bug, feel free to [open an
issue]. Or go ahead and [open a pull request] to contribute code. In order to
reduce the burden on our maintainers, please make sure that your code follows
our style guidelines outlined below.

<!-- prettier-ignore -->
[open an issue]: https://github.com/DSD-DBS/capella-model-explorer/issues
[open a pull request]: https://github.com/DSD-DBS/capella-model-explorer/pulls

## Developing

Use [uv](https://docs.astral.sh/uv/) to set up a local development environment.

Additionally, you need to have `pnpm` installed to build the JS/CSS bundles,
and optionally Docker to build and run Docker images.

```sh
git clone https://github.com/DSD-DBS/capella-model-explorer
cd capella-model-explorer
uv sync
uv run cme pre-commit-setup

# You may need to explicitly activate the project venv
# to make code completion and tools available:
source .venv/bin/activate.sh  # for Linux / Mac
.venv\Scripts\activate  # for Windows
```

You can use `uv run <tool>` to avoid having to manually activate the project
venv. For example, to view the built-in help for the `cme` command, run:

```sh
uv run cme --help
```

We additionally recommend that you set up your editor / IDE as follows.

- Indent with 4 spaces per level of indentation

- Maximum line length of 79 (add a ruler / thin line / highlighting / ...)

- _If you use Visual Studio Code_: Consider using a platform which supports
  third-party language servers more easily, and continue with the next point.

  Note that the Pylance language server is not recommended, as it occasionally
  causes false-positive errors for perfectly valid code.

- _If you do not use VSC_: Set up your editor to use the [python-lsp-server]
  and [ruff], and make sure that the relevant pylsp plugins are installed.

  [python-lsp-server]: https://github.com/python-lsp/python-lsp-server
  [ruff]: https://github.com/astral-sh/ruff

  You can install everything that's needed into the virtualenv with pip:

  ```sh
  pip install "python-lsp-server" pylsp-mypy ruff
  ```

  This will provide as-you-type linting as well as automatic formatting on
  save. Language server clients are available for a wide range of editors, from
  Vim/Emacs to PyCharm/IDEA.

Always modify the style via TailwindCSS classes within the Python code.

If not possible (because of collision with TailwindCSS' `prose` class), modify
the file `frontend/input.css` directly.

## Code style

We base our code style on a modified version of the
[Google style guide for Python code](https://google.github.io/styleguide/pyguide.html).
The key differences are:

- **Docstrings**: The [Numpy style guide] applies here.

  [numpy style guide]: https://numpydoc.readthedocs.io/en/latest/format.html#docstring-standard

  When writing docstrings for functions, use the imperative style, as per
  [PEP-257]. For example, write "Do X and Y" instead of "Does X and Y".

  [pep-257]: https://peps.python.org/pep-0257/

- **Overridden methods**: If the documentation did not change from the base
  class (i.e. the base class' method's docstring still applies without
  modification), do not add a short docstring á la "See base class". This lets
  automated tools pick up the full base class docstring instead, and is
  therefore more useful in IDEs etc.

- **Linting**: Use [ruff] for static code analysis, and [mypy] for static
  type checking.

  [mypy]: https://github.com/python/mypy

- **Formatting**: Use [ruff] as code auto-formatter. The maximum line length
  is 79, as per [PEP-8]. This setting should be automatically picked up from
  the `pyproject.toml` file. The reason for the shorter line length is that it
  avoids wrapping and overflows in side-by-side split views (e.g. diffs) if
  there's also information displayed to the side of it (e.g. a tree view of the
  modified files).

  [pep-8]: https://www.python.org/dev/peps/pep-0008/

  Be aware of the different line length of 72 for docstrings. We currently do
  not have a satisfactory solution to automatically apply or enforce this.

  Note that, while you're encouraged to do so in general, it is not a hard
  requirement to break up long strings into smaller parts. Additionally, never
  break up strings that are presented to the user in e.g. log messages, as that
  makes it significantly harder to grep for them.

- **Typing**: We do not make an exception for `typing` imports. Instead of
  writing `from typing import SomeName`, use `import typing as t` and access
  typing related classes like `t.TypedDict`.

  Use the new syntax and classes for typing introduced with Python 3.10.
  - Instead of `t.Tuple`, `t.List` etc. use the builtin classes `tuple`, `list`
    etc.
  - For classes that are not builtin (e.g. `Iterable`),
    `import collections.abc as cabc` and then use them like `cabc.Iterable`.
  - Use [PEP-604-style unions], e.g. `int | float` instead of
    `t.Union[int, float]`.
  - Use `... | None` (with `None` always as the last union member) instead of
    `t.Optional[...]` and always explicitly annotate where `None` is possible.

  [pep-604-style unions]: https://www.python.org/dev/peps/pep-0604/

- **Python style rules**: The auto-formatter wins.

- When working with `dict`s, consider using `t.TypedDict` instead of a more
  generic `dict[str, float|int|str]`-like annotation where possible, as the
  latter is much less precise (often requiring additional `assert`s or
  `isinstance` checks to pass) and can grow unwieldy very quickly.

- Prefer `t.NamedTuple` over `collections.namedtuple`, because the former uses
  a more convenient `class ...:` syntax and also supports type annotations.
