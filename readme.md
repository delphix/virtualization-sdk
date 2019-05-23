# Welcome to the New Face of Delphix Docs

Delphix Docs are embarking on a great-- nay, a noble quest. It is a quest to break the shackles of Confluence once and for all, and usher in an era of prosperity and great documentation... with Markdown.

## Installation

Please have a look through the following requirements and steps. If you're impatient and want to just run quick commands to get it done, scroll to [Quick Steps](#quick-steps)

### Clone this repo

Open your terminal, ```cd``` to whatever top level directory you want and paste:

`git clone git@gitlab.delphix.com:docs/virt-sdk-docs.git`

Now we need to get Python 3 installed. If you already have it installed, you can skip ahead to [Install pipenv](#install-pipenv). If you are a savvy adventurer in Pythonland and already have `pipenv` installed, skip to [Set up your environment](#set-up-your-environment).

### Install Python 3

The fastest way to do this on OSX is to install Homebrew and use it to install python3.

1. Install homebrew if it's not already installed: `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

2. Update homebrew: `brew update`

3. Install python3: `brew install python3`


### Install pipenv

We'll be using `pipenv` to create a virtual build environment. If you're not familiar with `pipenv`, it combines pip package management along with a virtual environment into a simple Pipfile, which is included in this repo. To install `pipenv` (and upgrade pip), run this:

`pip3 install --upgrade pip pipenv`

### Set up your environment

Now that `pipenv` is installed, we can add in the packages necessary to run your own local docsdev. `cd` into the virt-sdk-docs folder created by your `git clone` command and run:

`pipenv install mkdocs`

Congratulations! You're all set up!

## Run Local Docsdev

To run your own local documentation development environment, make sure you're in the virt-sdk-docs folder and type:

`pipenv run mkdocs serve`

This will run a local `mkdocs` instance on your machine that serves up the documentation at http://localhost:8000/

From here you can make any changes you want to the .md (markdown) files inside virt-sdk-docs/docs, and the `mkdocs` server will update with your changes on the fly. Easy, good old fashioned editing. 

## ADVANCED: Tinkering with mkdocs

If you really want to get in and do any custom mkdocs development, you can enter a virtualenv shell rather than running mkdocs through the `pipenv run` command. Just run:

`pipenv shell`

This will activate the virtualenv in which you can run `mkdocs serve` or whatever else you want. You can deactivate/exit the shell with the `exit` command or CTRL+D.

## Quick Steps

1. `git clone git@gitlab.delphix.com:docs/virt-sdk-docs.git && cd virt-sdk-docs`
2. `/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`
3. `brew update && brew install python3`
4. `pip3 install --upgrade pip pipenv`
5. `pipenv install`
6. `pipenv run mkdocs serve`

## Running mkdocs after install

When you need to start your local mkdocs server, it's really simple. Just make sure you're in the 'virt-sdk-docs' directory locally (e.g. `cd ~/virt-sdk-docs`), then run: `pipenv run mkdocs serve`
