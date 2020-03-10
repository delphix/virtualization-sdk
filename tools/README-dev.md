# Delphix Virtualization SDK Tools

## Purpose
The `tools` package represents a CLI of the Delphix Virtualization SDK. Plugin developers will install the CLI to build
and upload virtualization plugins. 

## Getting Started

### Development Environment
To setup the development environment, follow the instructions in [README-dev.md](https://github.com/delphix/virtualization-sdk/blob/develop/README-dev.md)

For quick iterations, install the `tools` package in editable mode (`pip install -e .`). This means that changes to the
code will automatically be reflected in your environment. You will not need to reinstall the tools module each time
a change is made.

Changes to the code can be tested using `dvp <options>`. `dvp` is the CLI tool that is built from the source here that
helps build and upload a plugin to DE.

### Adding a command
The CLI uses [Click](https://click.palletsprojects.com/en/7.x/). This is a decorator driven library that builds a full
CLI.

The starting point for the CLI is `virtualization._internal.cli:delphix_sdk`. This is annotated with the `@click.group`
annotation indicating there will be subcommands.

All that is needed to add a command is to define a new method in `virtualization._internal.cli`. **The method's name
will be the name of the command.** Annotate the method with `@delphix_sdk.command()`. It will automatically be added
as a subcommand. Look at the [Click documentation](https://click.palletsprojects.com/en/7.x/) to see other annotations
available to configure the command.

Click should be contained to `virtualization._internal.cli`. The implementation of the method should call immediately
into a method in another module. `virtualization._internal.cli` is the single source of truth for our CLI and should not
contain any business logic.

### Testing

#### Manual testing
It's easy to manually test the CLI as you can invoke different SDK CLI commands from command line. 

To test the build command, run `dvp build --dev`.

When you run `dvp build`, the wrappers are built with the plugin. This builds `common`, `libs`, and `platform`
locally and bundles them with the plugin. If you don't pass `--dev` flag, `dvp build` will search for wrappers on PyPI. 
To enable building wrappers from source instead, a special configuration entry is needed in your dvp config file which
is located at `~/.dvp/config`:

```
[dev]
vsdk_root = /path/to/vsdk_repo_root
```

#### Unit and functional (blackbox) testing
Refer to [README-dev.md](https://github.com/delphix/virtualization-sdk/blob/develop/README-dev.md). 

## Decisions

### CLI
We chose [Click](https://click.palletsprojects.com/en/7.x/) to build our CLI. It is simple, powerful, and dramatically
reduces the amount of code we would have to write if we used argparse. Click is more limiting in ways. It is opinionated
and not completely flexible. This is a limitation we're okay with. The benefits of having a feature full library out way
the risks. Our CLI is also relatively simple which reduces the impact of using an opinionated library.

We looked at cement. This was heavier weight and only supported Python 3. We also looked at argparse, but chose Click
due to the reasons above.

### Testing
We chose [PyTest](https://docs.pytest.org/en/latest/) in combination with [coverage](https://pytest-cov.readthedocs.io/en/latest/). 
The builtin unittest is the other popular option. PyTest seems to be more popular and flexible. It was also recommended
internally by people at Delphix. This is a decision we can revisit if we see that PyTest is insufficient.

### Formatting
We chose [yapf](https://github.com/google/yapf) as our formatter. It's easy and does what we want right out of the box. 
We would like to use [black](https://github.com/ambv/black) as this is what the QA gate uses but it only supports Python 3.

