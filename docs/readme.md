# Virtualization SDK Repository

This is the Markdown-based documentation for the Virtualization SDK.

## Important Note On Building Docs

As of this writing, the rest of the Virtualization SDK codebase is based on Python 2.
However, our docs infrastructure is based on Python 3! So, **all of the below commands
must be run in a Python 3 environment**.  It's recommended to use a totally separate
virtual environment for docs work than the one you use in the rest of the SDK codebase.

## Local Testing
Install dependencies for building documentation and run `pipenv run mkdocs serve`

```
$ pipenv install
Installing dependencies from Pipfile.lock (cf5b7c)...
  🐍   ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉ 16/16 — 00:00:02
To activate this project's virtualenv, run pipenv shell.
Alternatively, run a command inside the virtualenv with pipenv run.

$ pipenv run mkdocs serve
INFO    -  Building documentation...
INFO    -  Cleaning site directory
[I 200424 15:54:06 server:292] Serving on http://127.0.0.1:8000
[I 200424 15:54:06 handlers:59] Start watching changes
[I 200424 15:54:06 handlers:61] Start detecting changes
```

The docs would be served up at [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Debugging

#### mkdocs not found
```
$ pipenv run mkdocs serve
Error: the command mkdocs could not be found within PATH or Pipfile's [scripts].
```
Run `pipenv install` to make sure all the dependencies are installed from the Pipfile.

#### setuptools incompatibility
```
$ pipenv install
Installing dependencies from Pipfile.lock (65135d)…
An error occurred while installing markupsafe==1.0 --hash=sha256:a6be69091dac236ea9c6bc7d012beab42010fa914c459791d627dad4910eb665! Will try again.
  🐍   ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉ 14/14 — 00:00:10
Installing initially failed dependencies…
[pipenv.exceptions.InstallError]:   File "/usr/local/lib/python3.7/site-packages/pipenv/core.py", line 1874, in do_install
[pipenv.exceptions.InstallError]:       keep_outdated=keep_outdated
[pipenv.exceptions.InstallError]:   File "/usr/local/lib/python3.7/site-packages/pipenv/core.py", line 1253, in do_init
[pipenv.exceptions.InstallError]:       pypi_mirror=pypi_mirror,
[pipenv.exceptions.InstallError]:   File "/usr/local/lib/python3.7/site-packages/pipenv/core.py", line 859, in do_install_dependencies
[pipenv.exceptions.InstallError]:       retry_list, procs, failed_deps_queue, requirements_dir, **install_kwargs
[pipenv.exceptions.InstallError]:   File "/usr/local/lib/python3.7/site-packages/pipenv/core.py", line 763, in batch_install
[pipenv.exceptions.InstallError]:       _cleanup_procs(procs, not blocking, failed_deps_queue, retry=retry)
[pipenv.exceptions.InstallError]:   File "/usr/local/lib/python3.7/site-packages/pipenv/core.py", line 681, in _cleanup_procs
[pipenv.exceptions.InstallError]:       raise exceptions.InstallError(c.dep.name, extra=err_lines)
[pipenv.exceptions.InstallError]: ['Collecting markupsafe==1.0', '  Using cached MarkupSafe-1.0.tar.gz (14 kB)']
[pipenv.exceptions.InstallError]: ['ERROR: Command errored out with exit status 1:', '     command: /Users/asarin/Documents/repos/github/virtualization-sdk/docs/env/bin/python3.7 -c \'import sys, setuptools, tokenize; sys.argv[0] = \'"\'"\'/private/var/folders/fg/d4zl41bs6wv97zpzq9gckxsm0000gn/T/pip-install-txi66ppe/markupsafe/setup.py\'"\'"\'; __file__=\'"\'"\'/private/var/folders/fg/d4zl41bs6wv97zpzq9gckxsm0000gn/T/pip-install-txi66ppe/markupsafe/setup.py\'"\'"\';f=getattr(tokenize, \'"\'"\'open\'"\'"\', open)(__file__);code=f.read().replace(\'"\'"\'\\r\\n\'"\'"\', \'"\'"\'\\n\'"\'"\');f.close();exec(compile(code, __file__, \'"\'"\'exec\'"\'"\'))\' egg_info --egg-base /private/var/folders/fg/d4zl41bs6wv97zpzq9gckxsm0000gn/T/pip-pip-egg-info-cl5ykzbs', '         cwd: /private/var/folders/fg/d4zl41bs6wv97zpzq9gckxsm0000gn/T/pip-install-txi66ppe/markupsafe/', '    Complete output (5 lines):', '    Traceback (most recent call last):', '      File "<string>", line 1, in <module>', '      File "/private/var/folders/fg/d4zl41bs6wv97zpzq9gckxsm0000gn/T/pip-install-txi66ppe/markupsafe/setup.py", line 6, in <module>', '        from setuptools import setup, Extension, Feature', "    ImportError: cannot import name 'Feature' from 'setuptools' (/Users/asarin/Documents/repos/github/virtualization-sdk/docs/env/lib/python3.7/site-packages/setuptools/__init__.py)", '    ----------------------------------------', 'ERROR: Command errored out with exit status 1: python setup.py egg_info Check the logs for full command output.']
ERROR: ERROR: Package installation failed...
```

Install `setuptools==45` to get around a deprecated API in version 46.

```
$ pip install setuptools==45
Collecting setuptools==45
  Downloading setuptools-45.0.0-py2.py3-none-any.whl (583 kB)
     |████████████████████████████████| 583 kB 2.7 MB/s
Installing collected packages: setuptools
  Attempting uninstall: setuptools
    Found existing installation: setuptools 46.1.3
    Uninstalling setuptools-46.1.3:
      Successfully uninstalled setuptools-46.1.3
Successfully installed setuptools-45.0.0
(env) ~/Documents/repos/github/virtualization-sdk/docs$ pipenv install
Installing dependencies from Pipfile.lock (65135d)…
  🐍   ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉ 14/14 — 00:00:03
```

## Live Testing via Github Pages
To publish doc change to your individual fork for review, we use github pages. To set this up follow these following steps.

1. Create a new local branch named `gh-pages`.
2. Using the same virtual environment above run:
```
pipenv run mkdocs build --clean
```
This will generate the `site` directory which will contain all the gererated docs.
3. Copy all these files to the root directory of the virtualization-sdk repo and delete all other files.
4. Commit and push these changes to your individual fork.
5. Go to your individual virtualization-sdk repo's settings, scroll to the bottom and verify under the GitHub Pages section the `Source` is set to `gh-pages branch`.
6. Right above this will be a link explaining where your docs are published.

You can also utilize the GitHub workflow for publishing docs (`.github/workflows/publish-docs.yml`) associated with a pull request.
The workflow is present on the `develop` branch. Create a branch called `docs/x.y.z` off `develop` on your fork of the repository
to ensure that your docs branch triggers the workflow. If you have more than one `docs/x.y.z` branch in your fork,
you have to push your doc changes to the docs branch with the latest `x.y.z` version. Otherwise, the workflow won't run.
You also have to make sure to choose `gh-pages` branch on your fork as the [publishing source](https://help.github.com/en/github/working-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site#choosing-a-publishing-source).
Once you push doc changes to the `docs/.x.y.z` branch, the docs site should be available under
`<your-github-username>.github.io/virtualization-sdk` shortly after. You can see the status of publishing under
`https://github.com/<your-github-username>/virtualization-sdk/actions`. This is a fast way to give a preview of your
changes in a pull request.

## Workflow diagrams
We create workflow diagrams using a tool called `draw.io` which allows us to import/export diagrams in html format. If you want to add a diagram or edit an existing one, simply create or import the html file in `docs/References/html` into `draw.io` and make your desired changes. When you are done, select your diagram and export it as a png file. You can think of the html files as source code, and the png files as build artifacts. After this step, you will be prompted to crop what was selected. You'll want this box checked to trim the whitespace around the diagram. After the diagrams are exported, check in the updated html file to `docs/References/html` and png file to `docs/References/images`.
