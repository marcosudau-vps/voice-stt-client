"""OBS-060 - Build / packaging check, as far as the project provides for one.

``WP-OBS-060`` asks for a *"Build-/Packaging-relevante Pruefung soweit im
Projekt vorgesehen"*. The project builds a frozen Windows client with
PyInstaller from ``voice-stt-client.spec``. Running that build is not part of
this work package; what IS checkable — and what actually goes wrong when a new
package appears — is:

* is every new module **statically reachable** from ``app.py``, so PyInstaller's
  import analysis finds it without a ``hiddenimports`` entry;
* is every new module **versionable**, i.e. not swallowed by ``.gitignore``
  (OBS-050 finding F-1: the rule ``logs/`` hid the whole ``ui/logs/`` package);
* does the packaging configuration still stand unchanged by this work package.

Run:  python <this file>
Exit: 0 when every check passes, 1 otherwise.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    if (parent / "core" / "observability").is_dir():
        PROJECT_ROOT = parent
        break

FAILURES = []

V1_MODULES = [
    "core.observability",
    "core.observability.models",
    "core.observability.redaction",
    "core.observability.normalizer",
    "core.observability.ingress",
    "core.observability.health",
    "core.observability.manager",
    "core.observability.worker",
    "core.observability.storage.sqlite",
    "core.observability.sinks.jsonl_file",
    "core.observability.query.base",
    "core.observability.query.local",
    "core.observability.query.service",
    "core.observability.adapters.python_logging",
    "core.observability.adapters.server_live",
    "core.observability.adapters.client_events",
    "core.logging_settings_metadata",
    "ui.logs",
    "ui.logs.log_window",
    "ui.logs.log_page",
    "ui.logs.log_table_model",
    "ui.logs.log_filter_bar",
    "ui.logs.log_detail_view",
    "ui.logs.log_query_controller",
]


# Pure ``Protocol`` signature modules (CONTRACTS 5.5 / 11.1). Nothing imports
# them at run time - they exist so the implementations have a written contract
# to satisfy, and the OBS-010 contract test imports them by name. They are
# therefore correctly ABSENT from the frozen import graph, and listing them as
# a packaging requirement would be wrong.
TYPE_ONLY_MODULES = [
    "core.observability.storage.base",
    "core.observability.sinks.base",
]


def check(name, ok, detail=""):
    print(("[PASS] " if ok else "[FAIL] ") + name + ((" - " + detail) if detail else ""))
    if not ok:
        FAILURES.append(name)
    return ok


def module_path(dotted):
    candidate = PROJECT_ROOT.joinpath(*dotted.split("."))
    if candidate.is_dir():
        return candidate / "__init__.py"
    return candidate.with_suffix(".py")


def imports_of(path):
    """Every dotted module name this file imports, including inside functions.

    PyInstaller's analysis walks the AST rather than executing the module, so a
    function-level ``from ui.logs.log_window import LogWindow`` is found. This
    mirrors that.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return set()
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # relative import
                parts = list(path.relative_to(PROJECT_ROOT).with_suffix("").parts)
                # the PACKAGE this module lives in: for ``a/b/__init__.py``
                # that is ``a.b``, for ``a/b/c.py`` it is ``a.b``
                package = parts[:-1]
                # every extra dot climbs one level further up
                climb = node.level - 1
                base = package[:len(package) - climb] if climb else package
                target = ".".join(base + ([node.module] if node.module else []))
                found.add(target)
                for alias in node.names:
                    found.add(target + "." + alias.name)
            elif node.module:
                found.add(node.module)
                for alias in node.names:
                    found.add(node.module + "." + alias.name)
    return found


def reachable_from(entry):
    """Transitive closure of first-party imports starting at ``entry``."""
    seen = set()
    queue = [entry]
    while queue:
        current = queue.pop()
        if current in seen:
            continue
        seen.add(current)
        path = module_path(current) if current != "__main__" else PROJECT_ROOT / "app.py"
        if not path.exists():
            continue
        for name in imports_of(path):
            if not name.split(".")[0] in ("core", "ui", "app", "scripts"):
                continue
            if name in seen:
                continue
            if module_path(name).exists():
                queue.append(name)
            else:  # "from x import Symbol" -> keep the module part
                parent = name.rsplit(".", 1)[0]
                if parent not in seen and module_path(parent).exists():
                    queue.append(parent)
    return seen


def main():
    print("=== P-1  every V1 module is statically reachable from app.py ===")
    graph = reachable_from("app")
    graph.add("app")
    # a package counts as reached when any of its modules is reached: that is
    # how PyInstaller pulls in ``__init__.py`` too
    for name in sorted(graph):
        parts = name.split(".")
        for depth in range(1, len(parts)):
            parent = ".".join(parts[:depth])
            if module_path(parent).exists():
                graph.add(parent)
    missing = [name for name in V1_MODULES if name not in graph]
    check("P-1.1 all " + str(len(V1_MODULES)) + " runtime V1 modules are in the "
          "import graph of app.py (no hiddenimports entry needed)",
          not missing, "missing=" + str(missing))
    print("       modules in the graph: " + str(len(graph)))
    unexpected = [name for name in TYPE_ONLY_MODULES if name in graph]
    check("P-1.2 the two Protocol-only modules are correctly NOT in the runtime "
          "graph (nothing imports them; they are contract text)",
          not unexpected, "unexpectedly reachable=" + str(unexpected))

    print("")
    print("=== P-2  every V1 module actually imports ===")
    failed = []
    for dotted in V1_MODULES + TYPE_ONLY_MODULES:
        if dotted.startswith("ui."):
            continue  # needs Qt; covered by the OBS-050 contract tests
        completed = subprocess.run(
            [sys.executable, "-c", "import " + dotted],
            cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=120)
        if completed.returncode != 0:
            failed.append((dotted, completed.stderr.strip().splitlines()[-1:]))
    check("P-2.1 every non-Qt V1 module imports in a clean interpreter",
          not failed, str(failed))

    print("")
    print("=== P-3  every V1 module is versionable (.gitignore) ===")
    ignored = []
    for dotted in V1_MODULES + TYPE_ONLY_MODULES:
        path = module_path(dotted)
        if not path.exists():
            ignored.append((dotted, "file missing"))
            continue
        completed = subprocess.run(
            ["git", "check-ignore", "-q", str(path.relative_to(PROJECT_ROOT))],
            cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=60)
        if completed.returncode == 0:
            ignored.append((dotted, "ignored by .gitignore"))
    check("P-3.1 no V1 module is hidden by .gitignore (OBS-050 finding F-1)",
          not ignored, str(ignored))

    completed = subprocess.run(
        ["git", "check-ignore", "-q", "ui/logs/__pycache__"],
        cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=60)
    check("P-3.2 ui/logs/__pycache__ is still ignored (the negation is narrow)",
          completed.returncode == 0, "exit=" + str(completed.returncode))

    print("")
    print("=== P-4  the packaging configuration is untouched by OBS-060 ===")
    for name in ("voice-stt-client.spec", "scripts/pyinstaller_runtime_platform.py"):
        completed = subprocess.run(
            ["git", "status", "--short", "--", name],
            cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=60)
        check("P-4 " + name + " unchanged by this run",
              not (completed.stdout or "").strip(),
              (completed.stdout or "").strip())

    print("")
    print("       Note: the frozen build already neutralises the Windows WMI")
    print("       platform probe in scripts/pyinstaller_runtime_platform.py.")
    print("       That is the same probe that makes an unpatched test")
    print("       environment hang - see V1_TEST_RESULTS.md, section on the")
    print("       test environment.")

    print("")
    print("=" * 70)
    if FAILURES:
        print("FAILURES: " + str(len(FAILURES)))
        for name in FAILURES:
            print("  - " + name)
        return 1
    print("ALL PACKAGING CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
