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
- **Namespace packages:** all five packages share the `dlpx.virtualization` namespace via `pkgutil.extend_path` in each `__init__.py`, so the separately-installed packages import under one namespace. `platform/__init__.py` re-exports the public symbols — **only symbols exported there are part of the plugin-author API surface.**
- **Proto conversion:** authors never touch protobuf directly. Wrapper data classes implement `to_proto()` / `from_proto()` (operation classes also have `to_protobuf*` helpers); the operation groups' `_internal_*` methods do the protobuf conversion + input validation on the engine side.
- **Adding an operation:** define the constant in `platform/operation.py`, add the decorator + `_internal_*` wrapper to the relevant operations class, export any new public symbols from `platform/__init__.py`, add tests under `platform/src/test/python/`, and update `plugin_validator.py` if the operation should be required for a valid plugin.

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
- User config `~/.dvp/config`: `[defaults]` (engine/user/password) and `[dev]` (`vsdk_root` for local wrapper builds). Global flags `-v`/`--verbose`, `-q`/`--quiet`.

Key modules under `tools/src/main/python/dlpx/virtualization/_internal/` (verified to exist; purposes summarized):

| Module | Purpose |
| --- | --- |
| `cli.py` | Click group + subcommands (declarations only) |
| `commands/build.py` | Build: config validation, codegen, dependency packaging |
| `commands/upload.py` | Upload artifact to the engine + job polling |
| `commands/initialize.py` | Plugin scaffold generation (`dvp init`) |
| `commands/download_logs.py` | Log retrieval from the engine |
| `codegen.py` | Generates Python classes from the plugin's JSON schemas |
| `plugin_util.py` / `plugin_validator.py` / `plugin_importer.py` | Plugin config parsing, decorator/validation, dynamic import |
| `delphix_client.py` | HTTP client for the Delphix Engine REST API |

**Adding a CLI command:** add a `@delphix_sdk.command()` function in `cli.py`, put the logic in a new `commands/<cmd>.py`, add tests under `tools/src/test/python/.../commands/`.

## Conventions

- **Language**: Python 3.11. Maven-style `src/main/python` + `src/test/python` tree under `dlpx/virtualization/`.
- **Linting**: `flake8` (run via `build_project.sh -f`).
- **Formatting / imports**: `yapf` and `isort` (both in each package's `dev` extra).
- **Testing**: `pytest` (+ `pytest-cov`, `coverage`); `mock`; `httpretty` for HTTP stubbing. Tests live in `src/test/python/...` with per-package `conftest.py`. Provide tests with changes where appropriate.
- **Packaging**: `setuptools` build backend; metadata in each `pyproject.toml`. License is Apache-2.0; sibling-package version pins (e.g. `dvp-tools` → `dvp-libs`/`dvp-platform`) are kept in sync via `.bumpversion.cfg`.
- **Copyright header**: every source file carries `Copyright (c) <year> by Delphix. All rights reserved.` Use `<first_year>, <current_year>` for files edited across years.
- **Lint/format config**: `flake8`/`isort`/`yapf` run on **tool defaults** — there are no repo-level `[tool.flake8]`/`[tool.isort]`/`.flake8` overrides (only `[tool.coverage.run]` in `tools/pyproject.toml`).

## Exception Hierarchy

Each package defines its own exceptions (verified in each package's `exceptions.py` / classes):

- **`common`** — base types reused elsewhere: `PluginRuntimeError`, `IncorrectTypeError`, `PlatformError`.
- **`libs`** — remote-execution failures: `LibraryError`, `PluginScriptError`, `IncorrectArgumentTypeError`.
- **`platform`** — `UserError` plus operation-validation errors: `IncorrectReturnTypeError`, `OperationNotDefinedError`, `OperationAlreadyDefinedError`, `DecoratorNotFunctionError`, `IncorrectUpgradeObjectTypeError`, the `MigrationId*` errors, etc.
- **`tools`** — `SDKToolingError` (internal) and `UserError` (user-facing/actionable), plus CLI-specific errors (`BuildFailedError`, `SchemaValidationError`, `HttpError`, `PluginUploadJobFailed`, `PluginUploadWaitTimedOut`, …).

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

## CI, Gate & Release

- **CI (GitHub Actions):** the PR check `.github/workflows/pre-commit.yml` runs the **full `pytest` suite across Python 3.11 on Ubuntu, macOS, and Windows** for PRs targeting `master`/`develop`/`release`. It installs the five packages in dependency order (`common` → `libs` → `platform` → `tools`/`dvp`) with `--find-links` to TestPyPI for `dvp-api`. Keep tests green on all three OSes. (Despite its name, this workflow runs cross-OS pytest, not the pre-commit framework.)
- Other workflows: `publish-python-packages.yml` (publishes the five packages), `publish-docs.yml` (publishes docs); `dependabot.yml` manages dependency bumps.
- **Push gate:** `.hooksconfig` defines the Delphix gate for this repo — gatekeeper approval group, Slack push notifications, allowed Jira issue types per branch, and review/comment checks.
- **Manual release (Artifactory):** `sh bin/upload.sh` publishes to the internal dev PyPI (`dvp-local-pypi`); `sh bin/upload.sh --prod` to production (`delphix-local`). Requires `ARTIFACTORY_PYPI_USER` / `ARTIFACTORY_PYPI_PASS`; it reads the version from `.bumpversion.cfg` and uploads with `twine`.

## Contributing / Posting Code for Review

- Fork-based workflow: fork → clone → change → test → bump version → push to a branch on your fork → open a PR to `delphix/virtualization-sdk`.
- **PRs must be based on the current `master` branch** and apply without conflicts. (Default branch is `develop`; CI gates PRs to `master`/`develop`/`release`.)
- **Limit each PR to a single commit that resolves one issue** — squash and rebase onto `master`; for large changes, use a stack of logically independent patches.
- **Commit message format** (see `CONTRIBUTING.md`): start with the GitHub issue id and its title, e.g. `Fixes #123 Format of error is incorrect`, followed by an optional description (each line ≤ 72 chars). If it doesn't address an issue, describe the changes.
- Merges require approval from a **code owner** (per `CODEOWNERS`).
- Bugs and features are filed as **GitHub issues** on `delphix/virtualization-sdk` using the Bug Report / Feature Request templates.

## Relationship to app-gate

The Virtualization API protobuf messages (`dvp-api`) are **defined and published by the app-gate repo** (`appliance/server/virtualizationApi`); the wrappers here abstract them for plugin authors. Blackbox tests for this repo are driven from app-gate. Keep wrapper changes compatible with the `dvp-api` version they target.

## Plugin Operations Reference

> ⚠ **Verification note:** the decorator names and their operation groups below are **verified against the code** (`platform/_discovery.py` / `_linked.py` / `_virtual.py` / `_upgrade.py`). The **Required / Arguments / Returns** columns are taken from the public plugin-operations docs (https://developer.delphix.com/References/Plugin_Operations/) and were **not** re-verified line-by-line against the operation signatures in this pass — confirm there before relying on exact argument names/return types. Argument names are contractual (must match exactly). Also present in code but omitted from the tables: `linked.source_to_physical()` and `virtual.source_to_physical()`.

### Discovery
| Decorator | Required | Arguments | Returns |
|---|---|---|---|
| `discovery.repository()` | Yes | `source_connection` | `list[RepositoryDefinition]` |
| `discovery.source_config()` | Yes | `source_connection`, `repository` | `list[SourceConfigDefinition]` |

### Linked source (dSource)
| Decorator | Required | Arguments | Returns |
|---|---|---|---|
| `linked.pre_snapshot()` | No | `direct_source`\|`staged_source`, `repository`, `source_config`, `optional_snapshot_parameters` | None |
| `linked.post_snapshot()` | Yes | `direct_source`\|`staged_source`, `repository`, `source_config`, `optional_snapshot_parameters` | `SnapshotDefinition` |
| `linked.start_staging()` | No | `staged_source`, `repository`, `source_config` | None |
| `linked.stop_staging()` | No | `staged_source`, `repository`, `source_config` | None |
| `linked.status()` | No | `staged_source`, `repository`, `source_config` | `Status` (defaults `ACTIVE`) |
| `linked.worker()` | No | `staged_source`, `repository`, `source_config` | None |
| `linked.mount_specification()` | Yes (staged) | `staged_source`, `repository` | `MountSpecification` |
| `linked.source_size()` | No | `direct_source`\|`staged_source`, `repository`, `source_config` | numeric |

### Virtual source (VDB)
| Decorator | Required | Arguments | Returns |
|---|---|---|---|
| `virtual.initialize()` | No | `virtual_source`, `repository` | `SourceConfigDefinition` |
| `virtual.configure()` | Yes | `virtual_source`, `snapshot`, `repository` | `SourceConfigDefinition` |
| `virtual.unconfigure()` | No | `virtual_source`, `repository`, `source_config` | None |
| `virtual.reconfigure()` | Yes | `virtual_source`, `repository`, `source_config`, `snapshot` | `SourceConfigDefinition` |
| `virtual.cleanup()` | No | `virtual_source`, `repository`, `source_config` | None |
| `virtual.start()` / `virtual.stop()` | No | `virtual_source`, `repository`, `source_config` | None |
| `virtual.pre_snapshot()` | No | `virtual_source`, `repository`, `source_config` | None |
| `virtual.post_snapshot()` | Yes | `virtual_source`, `repository`, `source_config` | `SnapshotDefinition` |
| `virtual.mount_specification()` | Yes | `virtual_source`, `repository` | `MountSpecification` |
| `virtual.status()` | No | `virtual_source`, `repository`, `source_config` | `Status` (defaults `ACTIVE`) |
| `virtual.source_size()` | No | `virtual_source`, `repository`, `source_config` | numeric |

### Data migration (upgrade)
`upgrade.repository(migration_id)`, `upgrade.source_config(...)`, `upgrade.linked_source(...)`, `upgrade.virtual_source(...)`, `upgrade.snapshot(...)` — all optional; each takes the old object **as a plain dict** (property names match the previous schema verbatim) and returns a dict. Migrations run in `migration_id` order.

Behavioral notes (from the docs): `optional_snapshot_parameters` is `None` for scheduled-policy snapshots (set only on user-triggered syncs); `virtual.unconfigure()` runs on Refresh/Delete/Disable (not just Delete); `virtual.cleanup()` runs after `unconfigure()` in the Delete flow; `virtual.mount_specification()` is the most-triggered required op (Enable/Provision/Refresh/Rollback/Start); `MountSpecification.ownership_specification` is Unix-only and optional.

## Engine ↔ Plugin Data Flows

> ⚠ **Verification note:** these describe **engine-side orchestration** (app-gate / Delphix Engine) — the *order* in which the engine invokes plugin operations and how it stores results. They are **not** code in this repo and were **not** verified here; they're carried over from prior documentation. Confirm against the engine docs / SDD before relying on exact ordering or storage details. Useful as a starting map for "trace the full data flow before deciding where a change belongs."

- **dSource link:** `linked.mount_specification` → `linked.start_staging` → `linked.pre_snapshot` → engine ingests (DIRECT: engine pulls; STAGED: plugin controls transfer) → `linked.post_snapshot` returns a `SnapshotDefinition` the engine persists as snapshot metadata.
- **dSource sync:** `linked.pre_snapshot` (optional) → ingest → `linked.post_snapshot` (new snapshot on the timeflow).
- **VDB provision:** `virtual.mount_specification` → engine clones+mounts → `virtual.configure(virtual_source, snapshot, repository)` → returns `SourceConfigDefinition`.
- **VDB refresh:** `virtual.unconfigure` → `virtual.mount_specification` → `virtual.configure` (newer snapshot).
- **VDB rollback / enable:** `virtual.mount_specification` → `virtual.reconfigure(...)` (+ `virtual.status` to verify on enable).
- **VDB snapshot:** `virtual.pre_snapshot` (optional) → engine snapshots → `virtual.post_snapshot` → `SnapshotDefinition`.
- **VDB delete:** `virtual.stop` (if running) → `virtual.unconfigure` → `virtual.cleanup` → engine unmounts/destroys the clone.
- **Plugin upgrade:** for each stored object the engine calls the matching `upgrade.*` migration (old dict in → new dict out) in `migration_id` order.
