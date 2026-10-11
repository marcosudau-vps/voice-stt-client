"""Read-only V2 record validation, independent of package ID and verdict."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


def status_of(text: str) -> str | None:
    match = re.search(r"(?:\*\*Status:\*\*\s*|Status\s+\*\*)([A-Z][A-Z_]+)", text)
    return match.group(1) if match else None


def validate_records(block: Path, extra_paths=(), pr_summary: Path | None = None) -> dict:
    block = Path(block).resolve()
    errors: list[str] = []
    checked_paths: set[Path] = set()
    documents: set[Path] = set()
    links = 0

    def require(path: Path):
        path = path.resolve()
        checked_paths.add(path)
        if not path.is_file():
            errors.append(f"Missing file: {path}")
        return path

    def read_json(path: Path):
        require(path)
        try:
            return json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            errors.append(f"Invalid JSON: {path}: {exc}")
            return None

    state = read_json(block / "WORKFLOW_STATUS.json")
    manifest = read_json(block / "PLANUNG/EVIDENCE/package-manifest.json")
    if state is None or manifest is None:
        return {"result": "FAIL", "errors": errors}
    package_id = state.get("activePackage") or state.get("nextPackage")
    packages = [p for p in manifest.get("packages", []) if p.get("id") == package_id]
    if len(packages) != 1:
        errors.append(f"Expected one manifest entry for {package_id}, found {len(packages)}")
    else:
        package = packages[0]
        expected = state.get("packageStatus")
        if not expected or package.get("status") != expected:
            errors.append(f"Status mismatch: WORKFLOW_STATUS={expected}, manifest={package.get('status')}")
        specification = require(block / "PLANUNG" / package["path"])
        documents.add(specification)
        record = block / "30_AUSFUEHRUNG" / package_id
        index = record / "00_PAKET.md"
        if state.get("activePackage"):
            require(index)
            documents.update(record.rglob("*.md"))
        for path in (specification, index):
            if path.is_file():
                actual = status_of(path.read_text(encoding="utf-8-sig"))
                if actual != expected:
                    errors.append(f"Status mismatch: {path}: {actual} != {expected}")
        report = package.get("executionReport")
        if report:
            require(block / report)

    # These keys carry block-relative records. Do not treat historical status
    # words in run reports as active verdicts, or branch refs as file paths.
    def record_paths(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"source", "additionalCorrectionSource", "report", "evidence", "reviewReport"} and isinstance(item, str):
                    require(block / item)
                elif key != "relatedServerFix":
                    record_paths(item)
        elif isinstance(value, list):
            for item in value:
                record_paths(item)

    record_paths(state)
    for path in extra_paths:
        documents.add(require(Path(path)))
    for path in sorted(documents):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8-sig")
        text = re.sub(r"^\s*(`{3,}|~{3,}).*?^\s*\1\s*$", "", text, flags=re.M | re.S)
        # Inline Markdown destinations, including <paths with spaces>.
        destinations = re.findall(r"\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+\"[^\"]*\")?\s*\)", text)
        destinations += re.findall(r"^\s*\[[^\]]+\]:\s*(<[^>]+>|\S+)", text, re.M)
        for destination in destinations:
            destination = destination.strip("<>")
            parsed = urlsplit(destination)
            if parsed.scheme or destination.startswith(("#", "//")):
                continue
            if not parsed.path:
                continue
            links += 1
            target = (path.parent / unquote(parsed.path)).resolve()
            if not target.exists():
                errors.append(f"Broken link in {path}: {destination} -> {target}")
    if pr_summary is not None:
        require(pr_summary)
        if pr_summary.is_file():
            text = pr_summary.read_text(encoding="utf-8-sig")
            if package_id not in text or status_of(text) != state.get("packageStatus"):
                errors.append("PR summary package/status mismatch")
    return {
        "result": "FAIL" if errors else "PASS", "package": package_id,
        "packageStatus": state.get("packageStatus"), "referencedFiles": len(checked_paths),
        "markdownFiles": len(documents), "relativeLinks": links, "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--block", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--paths", type=Path, nargs="*", default=[])
    parser.add_argument("--pr-summary", type=Path, help="Locally saved current PR body; no network access")
    args = parser.parse_args()
    result = validate_records(args.block, args.paths, args.pr_summary)
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return int(result["result"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main())
