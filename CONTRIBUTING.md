# Virtualization SDK Contribution Guide

*First of all, thanks for taking the time to contribute to the virtualization-sdk project!*

By following these guidelines you can help us make this project even better.

# Table of Contents
[Getting Started](#getting-started)

[How to Build the SDK from Source](#how-to-build-the-sdk-from-source)

[Asking for Help](#asking-for-help)

[How to Contribute](#how-to-contribute)

  * [How to Raise Pull Requests](#how-to-raise-pull-requests)
  * [Code Owners](#code-owners)

[Testing and CI/CD](#testing-and-ci/cd)

[Coding Guidelines](#coding-guidelines)

  * [Commit Message Format](#commit-message-format)


## Getting Started
The virtualization-sdk is distributed as a Python package called [dvp](https://pypi.org/project/dvp/). Install it in your local development environment so that you can build and upload a plugin.


## How to Build the SDK from Source
The virtualization-sdk repository can be built from source on GitHub as described below.

### Fork the virtualization-sdk Repository

First step is to fork the virtualization-sdk repository. Please refer to [Forking a GitHub Repository](https://help.github.com/en/github/getting-started-with-github/fork-a-repo) for instructions.

### Clone the virtualization-sdk Repository

Once the virtualization-sdk repository is forked, clone the forked repository into a local copy on your computer. Please refer to [Cloning a Forked Repository](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository) for instructions.

`git clone git@github.com:your-username/virtualization-sdk.git`

### Development

For development instructions, refer to [README-dev.md](https://github.com/delphix/virtualization-sdk/blob/develop/README-dev.md).

## Asking for Help
Please raise a GitHub issue to ask for help with appropriate GitHub tag <TBD - Label for help>.

## How to Contribute

### How to Raise Pull Requests
This repository uses GitHub standard pull request model. Once the changes are made locally and committed to the forked repository and tested, a pull request can be raised using the pull request template <TBD - Link to pull-request template> for the changes to be reviewed.

Some guidelines for Pull Requests:

* All pull requests must be based on the current master branch and apply without conflicts.
* All GitHub Actions checks should succeed. Please refer to [Testing and CI/CD](#testing-and-cicd) for details.
* Please attempt to limit pull requests to a single commit which resolves one specific issue.
* Make sure your commit messages are in the correct format as specified at [Commit Message Format](#commit-message-format)
* When updating a pull request squash multiple commits into one and perform a rebase. You want all your changes to be included in one commit replayed on top of master branch of the virtualization-sdk.
* For large pull requests consider structuring your changes as a stack of logically independent patches which build on each other. This makes large changes easier to review and approve which speeds up the merging process.
* Try to keep pull requests simple. Simple code with comments is much easier to review and approve.
* Test cases should be provided when appropriate.

Once the pull request has required approvals from code owners of the repository, the code owner will merge the pull request into the actual virtualization-sdk repository.

### Code Owners
Code owners defined by the codeowners file in the repository are the gatekeepers of the repository. For a pull request to be merged, it requires approval from at least one codeowner.

## Testing and CI/CD
CI/CD for this repository is managed through GitHub Actions. All the checks need to succeed for the pull request to be merged.

## Coding Guidelines
### Commit Message Format
Commit messages for new changes must meet the following guidelines:
* Every commit message should have a GitHub issue id that it addresses and its title.
* Every commit message can have an optional Description of the issue. Though it is optional it is highly recommended to provide one to summarize important information about the fix.
* Each line of the description must be 72 characters or less.
* Sample commit message to address issue 123 with title "Format of error is incorrect":

    `Fixes #123 Format of error is incorrect`

    `Optional Description of the issue`
* If the commit doesn't address a specific issue, it should include a description of changes.


