# dependency-bump — dependency-bump configuration for virtualization-sdk

## Bot authors

- `app/dependabot`
- `app/mend-for-github-com`

## Version policy

`latest-stable`

## Build & verification

The repo's `bin/build_project.sh` builds + tests Python modules. It accepts `-m <module>` flags to target specific modules; with no `-m`, it runs all 5 modules (common, libs, platform, tools, dvp).

**dependency-bump must pass `-m <module>` for each module whose `pyproject.toml` was modified by the consolidation, but only for pass 2 (test/lint). Pass 1 (build) is never scoped with `-m` — it always builds all 5 modules.** If all 5 modules are affected, pass 2 also omits `-m`.

Run as **two passes**, never combined into one `-bctf` invocation — `common`/`libs`/`platform`/`dvp` don't declare `coverage`/`flake8` in their own `pyproject.toml` dev extras (only `tools` does), and `build_project.sh`'s `build_module()` only installs from that module's own `pyproject.toml` (modules are visited in the order given to `-m`, or common→libs→platform→tools→dvp when `-m` is omitted — either way, any module visited before `tools` still lacks `coverage`/`flake8`). A single combined, `-m`-scoped pass fails flake8/coverage on modules processed before `tools`'s dev extras are installed — confirmed live (build failed for common/libs/platform: "missing dev deps (coverage, flake8) — they weren't installed before tests ran"). The same reasoning is why pass 1 must never be `-m`-scoped either: if a batch only touches, say, `libs`, an `-m libs` build never installs `tools`' `pyproject.toml` and its `coverage`/`flake8` extras land nowhere, so pass 2's `-ctf -m libs` fails the same way.

1. **Pass 1 — build all 5 modules, unscoped** (this is what makes pass 2 safe — it installs every module's `pyproject.toml`, including `tools`' `coverage`/`flake8` extras, into the shared venv before any test/lint step runs, regardless of which modules the batch actually touched):
   ```
   sh bin/build_project.sh -b
   ```
2. **Pass 2 — coverage-instrumented tests + flake8**, scoped to the affected modules:
   ```
   sh bin/build_project.sh -ctf {-m <module> for each affected module, OR omit if all 5 affected}
   ```
   Still only **one** test execution (under coverage) — splitting build from verification does not reintroduce the double-test-run problem this two-pass structure originally had (that was the separate `-bt` then `-tc -f` structure, which ran the suite plain *and* under coverage; here `-b` never runs tests at all).

Examples (resolved by depbump at runtime based on what changed):

| Source PRs touch                                                | Resolved commands |
|-----------------------------------------------------------------|---|
| Only `libs/pyproject.toml`                                      | `sh bin/build_project.sh -b` then `sh bin/build_project.sh -ctf -m libs` |
| `libs` + `common`                                               | `sh bin/build_project.sh -b` then `sh bin/build_project.sh -ctf -m libs -m common` |
| All 5 modules (typical for pytest/zipp/packaging consolidation) | `sh bin/build_project.sh -b` then `sh bin/build_project.sh -ctf` |

A failure here is handled by the skill's own bounded fix-and-retry loop (initial attempt + up to 2 retries, then it stops and flags the batch for a human — see the `dependency-bump` skill's own `steps/build-and-automate.md`, not a file in this repo), not an unbounded retry — nothing in this config file controls that bound.

`docs` is not one of the 5 modules above — it has its own build via `mkdocs`, using `docs/Pipfile`/`Pipfile.lock` (pipenv), not `pyproject.toml`. If any dependency in this batch touches a `docs/` manifest, also run:

- `cd docs && pipenv sync && pipenv run mkdocs build --clean --strict`

`docs/Pipfile`'s `[dev-packages]` section is empty — `mkdocs`/`mkdocs-material`/`markdown-include`/`mkdocs-awesome-pages-plugin` all live under `[packages]` — so `pipenv sync` (no `--dev`) is what installs strictly from the refreshed `docs/Pipfile.lock`.

**Do not use `docs/build.sh` for verification.** It deploys straight to production (`aws s3 sync ./site s3://dlpx-virt-sdk-docs --delete ...`) as a side effect — running it here would publish an unreviewed, unmerged docs build and delete anything not in it. `mkdocs build --clean --strict` is the safe, no-side-effect verification analogue — deliberately stricter than `docs/build.sh`'s own `mkdocs build --clean` (no `--strict`), since `--strict` fails the build on broken links/config, which is exactly the breakage a docs dependency bump could introduce, without touching the live site.

## Lock files

`docs/Pipfile` is backed by `docs/Pipfile.lock` (pipenv) — a bumped version needs the lock refreshed, not just a text edit. For a direct dependency (a real line in `docs/Pipfile`, e.g. `mkdocs-material`), edit that line's version first, then run the refresh command below. For a transitive dependency (no line in `docs/Pipfile` — e.g. `pygments`, `pymdown-extensions`, `idna`, `urllib3`, all pulled in indirectly), make no edit at all and run only the refresh command; never use `pipenv update <dep>==<version>` here, since it adds the target as a new direct pin in `Pipfile` as a side effect, silently turning an indirect dependency into a declared one — a bare re-resolve is what stays scoped to the lock file:

- `docs/Pipfile.lock`: `cd docs && pipenv lock`

## Additional automations

The end-to-end smoke check below needs `~/.dvp/config` with a `[dev]` section setting `vsdk_root` to this checkout's absolute path (required for `--dev` builds — see this repo's `CLAUDE.md`, "Environment & Install" section). Run it from an isolated temp directory, not this checkout: `dvp init` (`--root-dir`, defaults to `os.getcwd()`) and `dvp build` (`-c`/`plugin_config.yml`, `-a`/`artifact.json`, both cwd-relative) resolve their paths against the current directory, so running them unscoped here would create `src/`, `schema.json`, `plugin_config.yml`, `artifact.json` in this repo and leave the batch's workspace dirty.

The blackbox suites below are deliberately narrower than this repo's `CLAUDE.md` "Testing Tiers" minimum (`appdata_python_samples` + `appdata_basic`) for regular PRs: `appdata_basic` alone is sufficient as a sanity check for a dependency-bump batch, and `virtualization_sdk` is added to catch a bumped dependency breaking `dvp` itself.

The flake8 run below assumes the unscoped `-b` from pass 1 above already installed `tools`' `flake8` extra into the shared venv in this session — don't run it standalone in a fresh venv without that prior build.

- `sh bin/build_project.sh -f {-m <module> for each affected module, OR omit if all 5}` [sync]
- `cd <temp-dir> && dvp init --root-dir . && dvp build --dev`, verify `artifact.json` is produced [sync]
- `"${CLAUDE_PLUGIN_ROOT}/skills/dependency-bump/scripts/trigger_blackbox.sh" {repo-url} {branch} virtualization_sdk APPDATA_SDK_UBUNTU20_STAGED_CENTOS73` [async]
- `"${CLAUDE_PLUGIN_ROOT}/skills/dependency-bump/scripts/trigger_blackbox.sh" {repo-url} {branch} appdata_basic APPDATA_PYTHON_STAGED_RHEL93` [async]

## JIRA

dependency-bump creates a tracking ticket BEFORE the commit, uses its ID in the commit message and PR title, then comments back on the ticket with the PR URL after merge.

- Project: `DLPX`
- Issue type: `Bug`
- Product group: `Virtualization Platform - vSDK`
- Story points: 1

Commit message format: `<JIRA-ID> <JIRA-SUMMARY>` (single line). Example:

```
DLPX-12345 depbump: bump pytest from 9.0.2 to 9.0.3 (consolidates 9 PRs)
```

## Ignore

Nothing