# Delphix Virtualization SDK Tools

## Purpose
These tools will be one piece of the Delphix Virtualization SDK. Plugin developers will install these tools locally and use them to develop, build, and ship virtualization plugins.

## NOTE
This guide assumes that the current working directory is the root of the tools directory where this README is.

## The absolute basics
- `../gradlew dev && source activate-dev27` to get started developing
- `../gradlew precommit` must pass for code reviews. Copy and paste the output into reviews

## Getting Started

### Development Environment
To setup a development environment:

`../gradlew dev`

This task will take roughly 5 minutes to run, but needs to be ran rarely. This task pulls in Python source code, compiles it, and then pulls in some other binaries. We do this to ensure everyone has the identical system to make development simpler. Once that is done, the task creates a virtual environment and links the activate script to the tools root. If you aren’t familiar with virtualenv, take a look at [this guide.](https://www.dabapps.com/blog/introduction-to-pip-and-virtualenv-python/)

Once the task has completed, there will be a symlink to the virtualenv’s activate script in TOOLS_ROOT. Activate it:

`source activate-dev27`

You’re ready to start developing.

The development environment will already have all development and production dependencies installed in it. The tools module will be installed in ‘editable’ mode. This means that changes to the code will automatically be reflected in your environment. You will not need to reinstall the tools module each time a change is made.

NOTE: If you run into: `ERROR: The Python zlib extension was not compiled. Missing the zlib?` this is because you're missing a piece of XCode. Install the requirements listed [here](https://github.com/pyenv/pyenv/wiki/Common-build-problems).

#### virtualenv care
For the most part, the virtual environment should be managed through gradle. However, it is just a virtual environment at the end of the day. Anything can be installed into it. Be careful with this. If a new dependency is added it may work on one development environment but not another unless it’s been added to the dependencies specified in the Gradle build file.

`../gradlew clear` will recreate your virtualenv without needing to download the Python source code and compile it.

If you run a `clear` you can reinstall development dependencies with `../gradlew installDevDependencies`. The CLI will not be installed, however. This can be done with `../gradlew installProject`.

#### PyCharm
Feel free to use whichever IDE you want. PyCharm makes iterating and executing tests particularly easy. PyCharm needs to be setup with the Python binary from the virtualenv otherwise dependencies will not be configured correctly.

TODO: commands here

## Adding a command
The CLI uses [Click](https://click.palletsprojects.com/en/7.x/). This is a decorator driven library builds a full CLI.

The starting point for the CLI is `virtualization._internal.cli:delphix_sdk`. This is annotated with the `@click.group` annotation indicating there will be subcommands.

All that is needed to add a command is to define a new method in `virtualization._internal.cli`. **The method's name will be the name of the command.** Annotate the method with `@delphix_sdk.command()`. It will automatically be added as a subcommand. Look at the [Click documentation](https://click.palletsprojects.com/en/7.x/) to see other annotations available to configure the command.

Click should be contained to `virtualization._internal.cli`. The implementation of the method should call immediately into a method in another module. `virtualization._internal.cli` is the single source of truth for our CLI and should not contain any business logic.

## Committing Code
`../gradlew precommit` must pass for code to be committed. This does three things at a high level: lint, format, and test. This will actually format the whitespace in both the src and test directories and organize imports. All tests will be executed and coverage will be printed.

The output of this command should be copied and pasted into reviews until we get to a point that we can enforce these standards programmatically.

## Distribution
`../gradlew build` will create the production distribution.

## Decisions

### CLI
We chose [Click](https://click.palletsprojects.com/en/7.x/) to build our CLI. It is simple, powerful, and dramatically reduces the amount of code we would have to write if we used argparse. Click is more limiting in ways. It is opinionated and not completely flexible. This is a limitation we're okay with. The benefits of having a feature full library out way the risks. Our CLI is also relatively simple which reduces the impact of using an opinionated library.

We looked at cement. This was heavier weight and only supported Python 3. We also looked at argparse, but chose Click due to the reasons above. 

### Testing
We chose [PyTest](https://docs.pytest.org/en/latest/) in combination with [coverage](https://pytest-cov.readthedocs.io/en/latest/). The builtin unittest is the other popular option. PyTest seems to be more popular and flexible. It was also recommended internally by people at Delphix. This is a decision we can revisit if we see that PyTest is insufficient.

### Formatting
We chose [yapf](https://github.com/google/yapf) as our formatter. It's easy and does what we want right out of the box. We would like to use [black](https://github.com/ambv/black) as this is what the QA gate uses but it only supports Python 3.

### virtualenv managmenet
We chose JetBrain's [Gradle Python Envs](https://github.com/JetBrains/gradle-python-envs) plugin. This has some major limitations. It downloads Python source code and compiles it. This leads to long setup times. It also only does virtualenv management. Functionality to execute python inside of the virtual environment is left to us to build. For example, in order to run tests in both Python 2 and Python 3 we would need to write logic to active the Python 2 venv, run the tests, deactivate the Python 2 venv, active the Python 3 venv, run the tests, and finally deactivate the Python 3 venv all the while keeping track of where each binary is for each venv. This quickly leads to complex build files.

However, there aren't many other solutions to create reproducible development environments. Pipfile is great when deploying an application, but does not work very well when you're shipping a library. pipsi is designed to isolate applications. It's something a _user_ of the CLI might opt into, but doesn't work as well for development.

Additionally, the QA and devops gates use this plugin. We would all like to move off of it, but figured it was better to move off one technology than multiple.