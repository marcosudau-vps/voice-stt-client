"""Read-only-Prüfung des Belegsatzes, unabhängig von der früheren externen Ablage.

Mit dem Projekt-Python aufrufen. Prüft alle Dateien, sämtliche Archivquellen
und Markdown-Dateilinks; verändert weder Belege noch Git oder Benutzerprofile.
"""

import hashlib
import io
import json
from pathlib import Path
import re
from urllib.parse import unquote
import zipfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "IMPORT_MANIFEST.json").read_text(encoding="utf-8-sig"))
    actual = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    expected = {item["path"] for item in manifest["files"]} | {"IMPORT_MANIFEST.json"}
    assert actual == expected, {"missing": sorted(expected - actual), "unexpected": sorted(actual - expected)}
    for item in manifest["files"]:
        data = (root / item["path"]).read_bytes()
        assert digest(data) == item["sha256"] or digest(data.replace(b"\r\n", b"\n")) == item["sha256NormalizedLF"], item["path"]
    history = root / "HISTORIE"
    archive_manifest = json.loads((history / "QUELLBESTAND_MANIFEST.json").read_text(encoding="utf-8-sig"))
    parts = []
    for item in archive_manifest["archiveParts"]:
        data = (history / item["path"]).read_bytes()
        assert len(data) == item["bytes"] and digest(data) == item["sha256"], item["path"]
        assert len(data) < 100 * 1024 * 1024
        parts.append(data)
    archive_data = b"".join(parts)
    del parts
    assert len(archive_data) == archive_manifest["archiveBytes"]
    assert digest(archive_data) == archive_manifest["archiveSha256"]
    with zipfile.ZipFile(io.BytesIO(archive_data)) as archive:
        records = archive_manifest["files"]
        assert set(archive.namelist()) == {item["path"] for item in records}
        for item in records:
            data = archive.read(item["path"])
            assert len(data) == item["bytes"] and digest(data) == item["sha256"], item["path"]
    links = 0
    for path in root.glob("*.md"):
        for raw in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", path.read_text(encoding="utf-8-sig")):
            if raw.startswith(("http:", "https:", "#")):
                continue
            target = unquote(raw.split("#")[0].strip("<>"))
            assert (path.parent / target).exists(), (path.name, target)
            links += 1
    prompt = (root / "KORREKTURPROMPT_AP_CV2_000.md").read_text(encoding="utf-8")
    assert "_workflow-tools" not in prompt
    assert "work/client-v2/ap-cv2-000" in prompt and "/pull/2" in prompt
    assert "kein separater" in prompt.lower()
    print(json.dumps({
        "result": "PASS", "bundleFiles": len(actual), "sourceArchiveFiles": len(records),
        "archiveParts": len(archive_manifest["archiveParts"]), "relativeLinksChecked": links,
        "externalSourceAccessRequired": False,
        "publicationClaimed": False, "productTestsClaimed": False,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
