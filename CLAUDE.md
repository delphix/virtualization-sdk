[//]: # (Copyright (c) 2026 by Delphix. All rights reserved.)

# CLAUDE.md

This file provides guidance to AI agents working with code in this repository.

## Project Overview

The **Delphix Virtualization SDK** — the Python toolkit plugin developers use to build AppData plugins for the Delphix Engine. The repo produces **five Python distributions** that are versioned and shipped together:

| Package (dist name) | Directory | Purpose |
| --- | --- | --- |
| `dvp` | `dvp/` | Umbrella/meta package |
| `dvp-common` | `common/` | Shared classes/exceptions used by `libs` + `platform` |
| `dvp-libs` | `libs/` | Runtime **Libs** API plugins call on the engine (`run_bash`/`run_powershell`/`run_expect`/`run_sync`, credential helpers) |
| `dvp-platform` | `platform/` | The **Plugin** programming model — `Plugin()` + Discovery/Linked/Virtual/Upgrade operations |
| `dvp-tools` | `tools/` | The `dvp` CLI (plugin build/test/distribution) |

Two conceptually distinct parts, with different workflows:

- **`tools`** — the SDK's CLI (`dvp`). Aids plugin development, testing, and distribution. Changes here are isolated from the Delphix Engine.
- **`common` / `libs` / `platform`** — collectively the **"wrappers"**: vanilla Python classes that abstract the Virtualization API protobuf messages (`dvp-api`, **published by app-gate**) away from plugin developers. This is the API plugin developers write against. Changes here affect the plugin build.

A plugin must package all its dependencies — including `dvp-api` and the wrappers — and `dvp build` does this automatically.

## Plugin Programming Model

This is the API the wrappers expose and what `platform`/`libs` code must keep stable for plugin authors:

- A plugin instantiates `Plugin()` (`from dlpx.virtualization.platform import Plugin`), composed of four operation groups (`platform/_plugin.py`): **`discovery`** (`_discovery.py`), **`linked`** (direct/staged linking, `_linked.py`), **`virtual`** (provisioning virtual datasets, `_virtual.py`), and **`upgrade`** (`_upgrade.py`).
- Authors implement an operation by decorating a method with the plugin object's group, e.g. `@my_plugin.virtual.configure()`, `@my_plugin.discovery.repository()`. The decorator name must start with the plugin variable's name.
- At runtime, plugin code calls the **`libs`** API (`from dlpx.virtualization.libs import ...`) to do remote work on the host: `run_bash` / `run_powershell` / `run_expect`, `run_sync` (rsync), and `retrieve_credentials` / `upgrade_password`.

## Repository Layout

- `common/`, `libs/`, `platform/`, `tools/`, `dvp/` — the five packages, each with its own `pyproject.toml`.
- Each package uses a **Maven-style source layout**:
  - main: `<pkg>/src/main/python/dlpx/virtualization/...`
  - tests: `<pkg>/src/test/python/dlpx/virtualization/...` (with a `conftest.py` per package)
- `bin/` — build/test tooling (`build_project.sh`).
- `docs/` — SDK documentation, built with **MkDocs** (Material theme; `docs/mkdocs.yml`) in its own `pipenv` env (`docs/Pipfile`); `docs/build.sh` runs `pipenv run mkdocs build` and publishes to S3. Public user docs live at https://developer.delphix.com.
- `.bumpversion.cfg` — version config spanning all five packages.

## Environment & Install

- **End users** install the published CLI from PyPI: `pip install dvp` (or `dvp==<version>`). Everything below is for SDK *developers*.
- **Python 3.11 only** (`requires-python = ">=3.11, <3.12"`; current series is vSDK 5.x). Develop in a Python 3.11 virtualenv.
- `dvp-api` is hosted on **TestPyPI**, so configure pip with an extra index. Create `<virtualenv-root>/pip.conf`:
  ```
  [install]
  index-url=https://pypi.org/simple/
  extra-index-url=https://test.pypi.org/simple/
  ```
- **Editable install of a single package** (with dev tooling): from the package directory,
  ```
  pip install -e ".[dev]"
  ```
  (The `dev` extra replaces the old `requirements.txt`-based dev install.)

## Build & Test Commands

All from the repo root via `bin/build_project.sh` (operates on `common`, `libs`, `platform`, `tools`, `dvp`):

```bash
sh bin/build_project.sh -h            # help
sh bin/build_project.sh -b            # build all modules
sh bin/build_project.sh -t            # run unit tests for all modules
sh bin/build_project.sh -f            # flake8 validation
sh bin/build_project.sh -c            # test-coverage mode
sh bin/build_project.sh -v            # verbose
sh bin/build_project.sh -m common     # restrict to module(s); repeatable: -m common -m libs
# flags combine, e.g.:
sh bin/build_project.sh -bt -m tools  # build + test just tools
sh bin/build_project.sh -bft -m tools # build + flake8 + test
sh bin/build_project.sh -bct -m tools # build + coverage + test
```

**Single package's unit tests** — from that package directory:
```bash
python -m pytest src/test/python
```

## CLI (`tools` / `dvp`)

- Built with **Click**. The console-script entry point (`tools/pyproject.toml` → `[project.scripts]`) is `dvp = "dlpx.virtualization._internal.cli:delphix_sdk"` (a `@click.group`). Add a subcommand by defining a method in `dlpx.virtualization._internal.cli` annotated `@delphix_sdk.command()` — the method name becomes the command name.
- **Keep Click confined to `cli.py`** — it's the single source of truth for the CLI and must hold **no business logic**; each command delegates immediately into a `_internal/commands/<cmd>.py` module.
- Commands: `dvp init` (scaffold a plugin), `dvp build` (bundle the plugin + wrappers + `dvp-api` into an upload artifact), `dvp upload` (push the artifact to a Delphix Engine), `dvp download-logs`.
- `dvp build` bundles the wrappers (`common`/`libs`/`platform`) with the plugin: pass `--dev` to build them **from source**, otherwise they're fetched from PyPI. Building from source also needs `~/.dvp/config`:
  ```
  [dev]
  vsdk_root = /path/to/virtualization-sdk
  ```
- Manually exercise the CLI with `dvp <command>` after an editable install of `tools`.

## Conventions

- **Language**: Python 3.11. Maven-style `src/main/python` + `src/test/python` tree under `dlpx/virtualization/`.
- **Linting**: `flake8` (run via `build_project.sh -f`).
- **Formatting / imports**: `yapf` and `isort` (both in each package's `dev` extra).
- **Testing**: `pytest` (+ `pytest-cov`, `coverage`); `mock`; `httpretty` for HTTP stubbing. Tests live in `src/test/python/...` with per-package `conftest.py`. Provide tests with changes where appropriate.
- **Packaging**: `setuptools` build backend; metadata in each `pyproject.toml`. License is Apache-2.0; sibling-package version pins (e.g. `dvp-tools` → `dvp-libs`/`dvp-platform`) are kept in sync via `.bumpversion.cfg`.
- **Copyright header**: every source file carries `Copyright (c) <year> by Delphix. All rights reserved.` Use `<first_year>, <current_year>` for files edited across years.
- **Lint/format config**: `flake8`/`isort`/`yapf` run on **tool defaults** — there are no repo-level `[tool.flake8]`/`[tool.isort]`/`.flake8` overrides (only `[tool.coverage.run]` in `tools/pyproject.toml`).

## Versioning

- All five packages (`dvp`, `dvp-common`, `dvp-libs`, `dvp-platform`, `dvp-tools`) are versioned and released **together**, using **semantic versioning** managed by **`bump2version`**.
- Version format: `MAJOR.MINOR.PATCH` (released) or `MAJOR.MINOR.PATCH.dev<N>` (dev builds); config in `.bumpversion.cfg`.
  ```bash
  bumpversion dev               # 1.1.0.dev7 -> 1.1.0.dev8
  bumpversion [major|minor|patch]
  bumpversion release           # 1.1.0.dev7 -> 1.1.0
  ```
- A bump updates the `[project].version` (and sibling-package pins) in all five `pyproject.toml`s **and** the `DVP_VERSION` constant in `tools/.../_internal/test_package_util.py` atomically — these targets are listed in `.bumpversion.cfg`. It does **not** commit or tag (`commit = False`, `tag = False`), so commit all the bumped files together yourself. Current version: `5.1.0`.

## Testing Tiers

1. **Unit** — `pytest` per package (or `build_project.sh -t`). No engine required.
2. **Manual** — wrapper changes are exercised by building a plugin, uploading to a Delphix Engine, and running standard workflows.
3. **Functional (blackbox)** — run from **app-gate** via `git blackbox` against your pushed SDK branch, e.g.:
   ```
   git blackbox -s appdata_python_samples \
     --extra-params="-p virt-sdk-repo=https://github.com/<user>/virtualization-sdk.git -p virt-sdk-branch=<branch>"
   ```
   **Minimum per PR**: `appdata_python_samples` and `appdata_basic` (direct or staged plugin). CLI-focused changes also run the `virtualization_sdk` suite. A non-dev version bump requires QA to create a matching `sdk-x-y-z` toolkit branch first.

## CI & Gate

- **CI (GitHub Actions):** the PR check `.github/workflows/pre-commit.yml` runs the **full `pytest` suite across Python 3.11 on Ubuntu, macOS, and Windows** for PRs targeting `master`/`develop`/`release`. It installs the five packages in dependency order (`common` → `libs` → `platform` → `tools`/`dvp`) with `--find-links` to TestPyPI for `dvp-api`. Keep tests green on all three OSes. (Despite its name, this workflow runs cross-OS pytest, not the pre-commit framework.)
- Other workflows: `publish-python-packages.yml` (publishes the five packages), `publish-docs.yml` (publishes docs); `dependabot.yml` manages dependency bumps.
- **Push gate:** `.hooksconfig` defines the Delphix gate for this repo — gatekeeper approval group, Slack push notifications, allowed Jira issue types per branch, and review/comment checks.

## Contributing / Posting Code for Review

- Fork-based workflow: fork → clone → change → test → bump version → push to a branch on your fork → open a PR to `delphix/virtualization-sdk`.
- **PRs must be based on the current `master` branch** and apply without conflicts. (Default branch is `develop`; CI gates PRs to `master`/`develop`/`release`.)
- **Limit each PR to a single commit that resolves one issue** — squash and rebase onto `master`; for large changes, use a stack of logically independent patches.
- **Commit message format** (see `CONTRIBUTING.md`): start with the GitHub issue id and its title, e.g. `Fixes #123 Format of error is incorrect`, followed by an optional description (each line ≤ 72 chars). If it doesn't address an issue, describe the changes.
- Merges require approval from a **code owner** (per `CODEOWNERS`).
- Bugs and features are filed as **GitHub issues** on `delphix/virtualization-sdk` using the Bug Report / Feature Request templates.

## Relationship to app-gate

The Virtualization API protobuf messages (`dvp-api`) are **defined and published by the app-gate repo** (`appliance/server/virtualizationApi`); the wrappers here abstract them for plugin authors. Blackbox tests for this repo are driven from app-gate. Keep wrapper changes compatible with the `dvp-api` version they target.
