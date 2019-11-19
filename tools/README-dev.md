# Delphix Virtualization SDK Tools

## Purpose
These tools will be one piece of the Delphix Virtualization SDK. Plugin developers will install these tools locally and use them to develop, build, and ship virtualization plugins.

## NOTE
This guide assumes that the current working directory is the root of the tools directory where this README is.

## The absolute basics
- `../gradlew build` to get started developing
- `../gradlew check` must pass for code reviews. Copy and paste the output into reviews

## Getting Started

### Development Environment
Development should be done in a personal virtualenv. To setup the virtual environment:

1. `virtualenv /path/to/env/root`. This should be a Python 2.7 virtualenv.
2. `source ~/path/ot/env/root/bin/activate`
3. `pip install -r lock.dev-requirements.txt`. This installs the required devlopment packages.
4. `../gradlew makeSetupPy` (this command will generate the setup.py file)
5. `pip install -e .`

NOTE: If build reports any issues with 'virtualenv' not found and/or errors finding virtualenv in the PATH, check and make sure virtualenv from Python 2.7 is being used and not from 3.x. Few places to check, for e.g. on Mac - /usr/local/bin/virtualenv, ~/Library/Python/2.7/virtualenv.

You’re ready to start developing.

The development environment will already have all development and production dependencies installed in it. The tools module will be installed in ‘editable’ mode. This means that changes to the code will automatically be reflected in your environment. You will not need to reinstall the tools module each time a change is made.

Changes to the code can be tested using `dvp <options>`. `dvp` is the CLI tool that is built from the source here that helps build and upload a plugin to DE.

NOTE: If you run into: `ERROR: The Python zlib extension was not compiled. Missing the zlib?` this is because you're missing a piece of XCode. Install the requirements listed [here](https://github.com/pyenv/pyenv/wiki/Common-build-problems).

## Adding a command
The CLI uses [Click](https://click.palletsprojects.com/en/7.x/). This is a decorator driven library builds a full CLI.

The starting point for the CLI is `virtualization._internal.cli:delphix_sdk`. This is annotated with the `@click.group` annotation indicating there will be subcommands.

All that is needed to add a command is to define a new method in `virtualization._internal.cli`. **The method's name will be the name of the command.** Annotate the method with `@delphix_sdk.command()`. It will automatically be added as a subcommand. Look at the [Click documentation](https://click.palletsprojects.com/en/7.x/) to see other annotations available to configure the command.

Click should be contained to `virtualization._internal.cli`. The implementation of the method should call immediately into a method in another module. `virtualization._internal.cli` is the single source of truth for our CLI and should not contain any business logic.

## Committing Code
`../gradlew check` and `../gradlew sdist` must pass for code to be committed. `check` does three things at a high level: lint, format, and test. This will actually format the whitespace in both the src and test directories and organize imports. All tests will be executed and coverage will be printed.

The output of `../gradlew check` command should be copied and pasted into reviews.

## Distribution
For distribution instructions, see the README in the root of this repository.

## Decisions

### CLI
We chose [Click](https://click.palletsprojects.com/en/7.x/) to build our CLI. It is simple, powerful, and dramatically reduces the amount of code we would have to write if we used argparse. Click is more limiting in ways. It is opinionated and not completely flexible. This is a limitation we're okay with. The benefits of having a feature full library out way the risks. Our CLI is also relatively simple which reduces the impact of using an opinionated library.

We looked at cement. This was heavier weight and only supported Python 3. We also looked at argparse, but chose Click due to the reasons above.

### Testing
We chose [PyTest](https://docs.pytest.org/en/latest/) in combination with [coverage](https://pytest-cov.readthedocs.io/en/latest/). The builtin unittest is the other popular option. PyTest seems to be more popular and flexible. It was also recommended internally by people at Delphix. This is a decision we can revisit if we see that PyTest is insufficient.

### Formatting
We chose [yapf](https://github.com/google/yapf) as our formatter. It's easy and does what we want right out of the box. We would like to use [black](https://github.com/ambv/black) as this is what the QA gate uses but it only supports Python 3.

