"""Create a verified GitHub release without a repository-sync stage.

The script determines the release version, runs the complete local test and
PyInstaller build gate, commits and pushes a version bump when necessary,
waits for CI on that exact commit, and only then creates and pushes the tag.
The tag starts ``.github/workflows/release.yml``, whose successful completion
creates the GitHub release and uploads the Windows executable.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

if __package__:
    from .build import REPO_ROOT, VERSION_FILE, read_version
else:
    from build import REPO_ROOT, VERSION_FILE, read_version


RELEASE_BRANCH = "main"
REPOSITORY = "marcosudau-vps/voice-stt-client"
CI_WORKFLOW = "ci.yml"
RELEASE_WORKFLOW = "release.yml"
CI_TIMEOUT_SECONDS = 45 * 60
RELEASE_TIMEOUT_SECONDS = 45 * 60
POLL_SECONDS = 15
VERSION_PATTERN = re.compile(r"\d+\.\d+\.\d+")


class Abort(RuntimeError):
    """A release precondition or verification gate failed."""


def step(text: str) -> None:
    print(f"\n=== {text}", flush=True)


def run(
    command: list[str],
    *,
    capture: bool = True,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> str:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=capture,
        encoding="utf-8",
        errors="replace",
        env=env,
        check=False,
    )
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip() if capture else ""
        raise Abort(f"{' '.join(command)} failed{f': {detail}' if detail else ''}")
    return result.stdout or ""


def parse_env_token(path: Path) -> str | None:
    if not path.is_file():
        return None
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == "GITHUB_TOKEN_VPS":
            token = value.strip().strip('"').strip("'")
            return token or None
    return None


def ensure_github_auth(env_file: Path | None) -> str | None:
    token = os.environ.get("GH_TOKEN")
    candidates = [env_file] if env_file else []
    candidates.append(Path.home() / "OneDrive" / "Desktop" / "github_accounts.env")
    if not token:
        for path in candidates:
            if path is None:
                continue
            token = parse_env_token(path)
            if token:
                os.environ["GH_TOKEN"] = token
                break
    if token:
        login = run(["gh", "api", "user", "--jq", ".login"]).strip()
        if login != "marcosudau-vps":
            raise Abort(f"GitHub token belongs to {login!r}, expected 'marcosudau-vps'")
        return token
    run(["gh", "auth", "status"])
    login = run(["gh", "api", "user", "--jq", ".login"]).strip()
    if login != "marcosudau-vps":
        raise Abort(
            "Authenticate gh as marcosudau-vps, set GH_TOKEN, or pass --env-file"
        )
    return None


def git_network_env(token: str | None) -> dict[str, str] | None:
    if not token:
        return None
    credentials = base64.b64encode(f"x-access-token:{token}".encode("ascii")).decode("ascii")
    env = os.environ.copy()
    env.update(
        {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "http.https://github.com/.extraheader",
            "GIT_CONFIG_VALUE_0": f"AUTHORIZATION: basic {credentials}",
        }
    )
    return env


def version_tuple(value: str) -> tuple[int, int, int]:
    if VERSION_PATTERN.fullmatch(value) is None:
        raise Abort(f"Invalid semantic version: {value!r}")
    return tuple(int(part) for part in value.split("."))  # type: ignore[return-value]


def next_patch(value: str) -> str:
    major, minor, patch = version_tuple(value)
    return f"{major}.{minor}.{patch + 1}"


def determine_release_version(current: str, tags: set[str]) -> str:
    semantic_tags = {
        tag[1:]
        for tag in tags
        if tag.startswith("v") and VERSION_PATTERN.fullmatch(tag[1:])
    }
    if semantic_tags and max(map(version_tuple, semantic_tags)) > version_tuple(current):
        raise Abort("VERSION is behind an existing release tag")
    if f"v{current}" not in tags:
        return current
    return next_patch(current)


def write_version(value: str, path: Path = VERSION_FILE) -> None:
    version_tuple(value)
    path.write_text(f"{value}\n", encoding="utf-8")


def check_tools() -> None:
    for name in ("git", "gh"):
        if shutil.which(name) is None:
            raise Abort(f"Required executable is unavailable: {name}")


def check_repository(token: str | None) -> None:
    branch = run(["git", "branch", "--show-current"]).strip()
    if branch != RELEASE_BRANCH:
        raise Abort(f"Releases must run from {RELEASE_BRANCH!r}, not {branch!r}")
    if run(["git", "status", "--porcelain"]).strip():
        raise Abort("The working tree is not clean")
    remote = run(["git", "remote", "get-url", "origin"]).strip()
    if not remote.rstrip("/").endswith(f"{REPOSITORY}.git"):
        raise Abort(f"Unexpected origin remote: {remote}")

    network_env = git_network_env(token)
    run(["git", "fetch", "origin", RELEASE_BRANCH, "--tags"], env=network_env)
    behind = run(["git", "rev-list", "--count", f"HEAD..origin/{RELEASE_BRANCH}"]).strip()
    ahead = run(["git", "rev-list", "--count", f"origin/{RELEASE_BRANCH}..HEAD"]).strip()
    if behind != "0" or ahead != "0":
        raise Abort(f"main is not synchronized with origin/main (ahead={ahead}, behind={behind})")
    visibility = run(["gh", "api", f"repos/{REPOSITORY}", "--jq", ".visibility"]).strip()
    if visibility != "public":
        raise Abort(f"Repository visibility is {visibility!r}, expected 'public'")


def all_tags() -> set[str]:
    return set(run(["git", "tag", "--list"]).split())


def run_local_gate() -> None:
    env = os.environ.copy()
    env.update(
        {
            "QT_QPA_PLATFORM": "offscreen",
            "OPENBLAS_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
        }
    )
    step("running the complete test suite")
    run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
        capture=False,
        env=env,
    )
    step("checking Python bytecode compilation")
    run(
        [sys.executable, "-m", "compileall", "-q", "app.py", "core", "ui", "scripts", "tests"],
        capture=False,
        env=env,
    )
    step("building and smoke-testing the Windows executable")
    run([sys.executable, "scripts/build.py", "--clean"], capture=False, env=env)


def wait_for_workflow(
    workflow: str,
    *,
    timeout_seconds: int,
    commit: str | None = None,
    branch: str | None = None,
) -> str:
    deadline = time.monotonic() + timeout_seconds
    last_status: str | None = None
    while time.monotonic() < deadline:
        command = [
            "gh", "run", "list", "--workflow", workflow, "--limit", "5",
            "--json", "status,conclusion,url,headSha,headBranch",
        ]
        if commit:
            command.extend(["--commit", commit])
        if branch:
            command.extend(["--branch", branch])
        raw = run(command, check=False)
        runs = json.loads(raw) if raw.strip().startswith("[") else []
        if commit:
            runs = [item for item in runs if item.get("headSha") == commit]
        if branch:
            runs = [item for item in runs if item.get("headBranch") == branch]
        if not runs:
            status = "waiting for run"
        else:
            info = runs[0]
            status = str(info.get("status"))
            if status == "completed":
                if info.get("conclusion") == "success":
                    return str(info.get("url") or "")
                raise Abort(f"{workflow} concluded {info.get('conclusion')}: {info.get('url')}")
        if status != last_status:
            print(f"  {workflow}: {status}", flush=True)
            last_status = status
        time.sleep(POLL_SECONDS)
    raise Abort(f"{workflow} did not finish within {timeout_seconds // 60} minutes")


def confirm(version: str) -> None:
    print(
        f"\nAbout to release v{version}:"
        "\n  * temporarily set VERSION and run all tests plus the PyInstaller build"
        "\n  * restore VERSION automatically if a local gate fails"
        "\n  * commit and push the version bump when needed"
        "\n  * wait for green CI on that exact commit"
        "\n  * only then push the tag and wait for the GitHub release"
    )
    if input("\nContinue? [y/N] ").strip().casefold() not in {"y", "yes", "j", "ja"}:
        raise Abort("Nothing was changed")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="run all local gates without changing Git")
    parser.add_argument("--yes", action="store_true", help="skip the final confirmation")
    parser.add_argument("--version", help="release an explicit MAJOR.MINOR.PATCH version")
    parser.add_argument("--env-file", type=Path, help="file containing GITHUB_TOKEN_VPS")
    args = parser.parse_args(argv)

    original_text: str | None = None
    version_changed = False
    committed = False
    try:
        check_tools()
        token = ensure_github_auth(args.env_file)
        check_repository(token)
        current = read_version()
        tags = all_tags()
        version = args.version or determine_release_version(current, tags)
        version_tuple(version)
        if f"v{version}" in tags:
            raise Abort(f"Tag v{version} already exists")
        if version_tuple(version) < version_tuple(current):
            raise Abort(f"Release version {version} is older than VERSION {current}")

        print(f"current version: {current}")
        print(f"release version: {version}")
        if not args.dry_run and not args.yes:
            confirm(version)

        original_text = VERSION_FILE.read_text(encoding="utf-8")
        if version != current:
            write_version(version)
            version_changed = True

        run_local_gate()
        if args.dry_run:
            if version_changed and original_text is not None:
                VERSION_FILE.write_text(original_text, encoding="utf-8")
                version_changed = False
            print(f"\nDry run passed; v{version} is ready for release.")
            return 0

        step("committing and pushing the verified version")
        if version_changed:
            run(["git", "add", "VERSION"])
            run(["git", "commit", "-m", f"release: v{version}"])
        committed = True
        network_env = git_network_env(token)
        run(["git", "push", "origin", RELEASE_BRANCH], capture=False, env=network_env)
        sha = run(["git", "rev-parse", "HEAD"]).strip()

        step(f"waiting for CI on {sha[:8]}")
        ci_url = wait_for_workflow(
            CI_WORKFLOW, timeout_seconds=CI_TIMEOUT_SECONDS, commit=sha
        )

        step(f"tagging v{version}")
        run(["git", "tag", "-a", f"v{version}", "-m", f"v{version}"])
        run(["git", "push", "origin", f"v{version}"], capture=False, env=network_env)

        step("waiting for the GitHub release workflow")
        release_run_url = wait_for_workflow(
            RELEASE_WORKFLOW,
            timeout_seconds=RELEASE_TIMEOUT_SECONDS,
            branch=f"v{version}",
        )
        release_url = run(
            ["gh", "release", "view", f"v{version}", "--repo", REPOSITORY, "--json", "url", "--jq", ".url"]
        ).strip()
        print(
            f"\nv{version} released successfully."
            f"\nCI: {ci_url}"
            f"\nRelease workflow: {release_run_url}"
            f"\nRelease: {release_url}"
        )
        return 0
    except Abort as exc:
        if version_changed and not committed and original_text is not None:
            VERSION_FILE.write_text(original_text, encoding="utf-8")
            print("Restored VERSION because the release did not reach a commit.", file=sys.stderr)
        print(f"\nrelease stopped: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        if version_changed and not committed and original_text is not None:
            VERSION_FILE.write_text(original_text, encoding="utf-8")
        print("\nrelease stopped", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
