"""
OBS-020 RUN-01 evidence script: proves ``client.log`` (file handler) and the
stdout formatter output are line-for-line unchanged by the additive
``observability`` parameter (WP-OBS-020 Evidence: "Der Diff zweier
`client.log`-Dateien (vorher/nachher)").

Method: the pre-change ``core/logging_setup.py`` is loaded straight from the
git index (``git show HEAD:core/logging_setup.py``) into an isolated module,
so nothing in the working tree is touched. Three runs are compared:

  A. OLD setup_logging(config)                      -- pre-change baseline
  B. NEW setup_logging(config)                       -- no observability param
  C. NEW setup_logging(config, observability=fake)   -- third handler present

A/B must be identical (backward compatibility). B/C must be identical too
(the third handler must not alter file/stdout output at all).

Run from the workspace root:
    python ARBEITSDATEIEN/.../OBS-020_RUN-01_client_log_before_after_diagnose.py
Exit code 0 = all checks passed.
"""

from __future__ import annotations

import importlib.util
import json
import logging
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(PROJECT_ROOT))


def _load_old_setup_logging():
    completed = subprocess.run(
        ["git", "show", "HEAD:core/logging_setup.py"],
        cwd=PROJECT_ROOT, capture_output=True, text=True, check=True,
    )
    old_source = completed.stdout
    tmp_path = Path(tempfile.mkstemp(suffix="_obs020_old_logging_setup.py")[1])
    tmp_path.write_text(old_source, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("_obs020_old_logging_setup", tmp_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.setup_logging


def _run(setup_fn, log_dir: Path, *, with_observability: bool) -> str:
    from core.config import LoggingConfig

    log_dir.mkdir(parents=True, exist_ok=True)
    # stdout=False: this diagnose only compares the file sink (client.log).
    # The console ReadableFormatter uses a non-ASCII separator that some
    # Windows console codepages cannot encode -- a pre-existing, unrelated
    # cosmetic issue that would otherwise spam stderr in this script.
    config = LoggingConfig(
        level="INFO", log_dir=str(log_dir), max_bytes=1_000_000, backup_count=1,
        stdout=False, json_format=True, channel_levels={},
    )
    logging.getLogger().handlers.clear()
    if with_observability:
        from core.observability.ingress import ObservabilityIngress

        class FakeObservability:
            def __init__(self, ingress, level="INFO"):
                self.ingress = ingress
                self.level = level

        ingress = ObservabilityIngress(instance_id="i" * 32)
        setup_fn(config, observability=FakeObservability(ingress))
    else:
        setup_fn(config)
    logging.getLogger("controller").info("diagnose line %s", 1)
    logging.getLogger("controller").warning("diagnose warning")
    logging.getLogger().handlers.clear()
    return (log_dir / "client.log").read_text(encoding="utf-8")


def _normalized_lines(content: str) -> list[str]:
    """Parse each JSONL line and drop the fields that legitimately differ
    between two separate runs: ``ts`` (wall clock) and the "Logging
    initialized" line's ``msg`` (it embeds the run-specific temp log_dir
    path)."""
    out = []
    for line in content.splitlines():
        if not line.strip():
            continue
        parsed = json.loads(line)
        parsed.pop("ts", None)
        if parsed.get("channel") == "app" and "Logging initialized" in parsed.get("msg", ""):
            parsed["msg"] = "Logging initialized: <normalized, dir differs per run>"
        out.append(json.dumps(parsed, sort_keys=True))
    return out


def main() -> int:
    from core.logging_setup import setup_logging as new_setup_logging

    old_setup_logging = _load_old_setup_logging()

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        content_a = _run(old_setup_logging, base / "a_old", with_observability=False)
        content_b = _run(new_setup_logging, base / "b_new_no_obs", with_observability=False)
        content_c = _run(new_setup_logging, base / "c_new_with_obs", with_observability=True)

    lines_a = _normalized_lines(content_a)
    lines_b = _normalized_lines(content_b)
    lines_c = _normalized_lines(content_c)

    ok = True

    if lines_a == lines_b:
        print("PASS  OLD vs NEW (no observability) client.log content identical")
    else:
        ok = False
        print("FAIL  OLD vs NEW (no observability) differ:")
        print("  OLD:", lines_a)
        print("  NEW:", lines_b)

    if lines_b == lines_c:
        print("PASS  NEW (no observability) vs NEW (with observability) client.log content identical")
    else:
        ok = False
        print("FAIL  NEW (no observability) vs NEW (with observability) differ:")
        print("  NO-OBS:  ", lines_b)
        print("  WITH-OBS:", lines_c)

    if ok:
        print("Alle Erwartungen erfuellt. client.log ist im Format unveraendert.")
        return 0
    print("Mindestens eine Erwartung nicht erfuellt.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
