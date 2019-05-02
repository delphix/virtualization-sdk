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
To setup a development environment:

`../gradlew build`

This task will take few minutes to run and does few things like setup the required python binaries, virtualenv, format source code and sort the imports.

Once the task has completed, check the output to setup recommended environment variables (e.g. export PATH=/Users/<usern name>/src/v-sdk/tools/build/pipsi/bin:$PATH). Next, setup virtualenv by running the following commands:

1. ../gradlew makeSetupPy (this command will regenerate the setup.py file that pipenv uses to create the local virtual environment)
2. `pipenv install -e .`

NOTE: If build reports any issues with 'virtualenv' not found and/or errors finding virtualenv in the PATH, check and make sure virtualenv from Python 2.7 is being used and not from 3.x. Few places to check, for e.g. on Mac - /usr/local/bin/virtualenv, ~/Library/Python/2.7/virtualenv.


You’re ready to start developing.

The development environment will already have all development and production dependencies installed in it. The tools module will be installed in ‘editable’ mode. This means that changes to the code will automatically be reflected in your environment. You will not need to reinstall the tools module each time a change is made.

Changes to the code can be tested using "pipenv run dvp <options>". 'dvp' is the CLI tool that is built from the source here that helps build and upload a plugin to DE. Alternatively, dvp can be run by doing the following -

1. Make sure 'pipenv install -e .' completes successfully.
2. Run 'pipenv shell' to activate the virtual environment created above in step 1.
3. Install dvp-common, dvp-libs, dv-platform packages (either from Artifactory or the respective local build/pyhton-dist directory) using the command `pip install <package file name>`.
3. Now, run dvp just like any other command, e.g. `dvp -h`
4. To exit out of the virtual environment shell, type `exit`.

NOTE: If you run into: `ERROR: The Python zlib extension was not compiled. Missing the zlib?` this is because you're missing a piece of XCode. Install the requirements listed [here](https://github.com/pyenv/pyenv/wiki/Common-build-problems).

#### virtualenv care
For the most part, the virtual environment should be managed through gradle. However, it is just a virtual environment at the end of the day. Anything can be installed into it. Be careful with this. If a new dependency is added it may work on one development environment but not another unless it’s been added to the dependencies specified in the Gradle build file.

`../gradlew clear` will recreate your virtualenv without needing to download the Python source code and compile it.

#### PyCharm
Feel free to use whichever IDE you want. PyCharm makes iterating and executing tests particularly easy. PyCharm needs to be setup with the Python binary from the virtualenv otherwise dependencies will not be configured correctly.

TODO: commands here

## Adding a command
The CLI uses [Click](https://click.palletsprojects.com/en/7.x/). This is a decorator driven library builds a full CLI.

The starting point for the CLI is `virtualization._internal.cli:delphix_sdk`. This is annotated with the `@click.group` annotation indicating there will be subcommands.

All that is needed to add a command is to define a new method in `virtualization._internal.cli`. **The method's name will be the name of the command.** Annotate the method with `@delphix_sdk.command()`. It will automatically be added as a subcommand. Look at the [Click documentation](https://click.palletsprojects.com/en/7.x/) to see other annotations available to configure the command.

Click should be contained to `virtualization._internal.cli`. The implementation of the method should call immediately into a method in another module. `virtualization._internal.cli` is the single source of truth for our CLI and should not contain any business logic.

## Committing Code
`../gradlew check` and `../gradlew sdist` must pass for code to be committed. `check` does three things at a high level: lint, format, and test. This will actually format the whitespace in both the src and test directories and organize imports. All tests will be executed and coverage will be printed.

The output of `../gradlew check` command should be copied and pasted into reviews.

## Distribution
Make sure `../gradlew build` reports success and then run `./gradlew sdist` from the root directory after making the SDK version change in build.gradle. This will make sure all dvp packages are created with the right version. Upload the SDK and dvp packages to Artifactory as described in the README.md file located at the root of the source repository.

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
