"""Einmaliger, rein lokaler Quellenimport; kein Gittransport und keine Produktänderung.

Aufruf: Projekt-Python sichere_quellbestand.py --source <Quellthema>
Keine impliziten externen Pfade. Alte Quellen werden ausschließlich gelesen.
Das Ergebnisarchiv ist historische Provenienz, keine operative Pflichtlektüre.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    destination = Path(__file__).resolve().parent
    if source == destination or source in destination.parents or destination in source.parents:
        raise SystemExit("Quelle und Ziel müssen getrennte Verzeichnisbäume sein.")
    history = destination / "HISTORIE"
    history.mkdir(exist_ok=True)
    archive_path = history / "WORKFLOW_TOOLS_THEMENSTAND_2026-10-11.zip"
    inventory_path = history / "QUELLBESTAND_MANIFEST.json"
    if archive_path.exists() or inventory_path.exists():
        raise SystemExit("Ein vorhandener Sicherungsstand wird nicht überschrieben.")
    files = sorted(path for path in source.rglob("*") if path.is_file())
    inventory = []
    with zipfile.ZipFile(archive_path, "x", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in files:
            resolved = path.resolve(strict=True)
            if source not in resolved.parents:
                raise SystemExit(f"Quellpfad außerhalb des Themas: {path.name}")
            data = path.read_bytes()
            relative = path.relative_to(source).as_posix()
            archive.writestr(relative, data)
            inventory.append({"path": relative, "bytes": len(data), "sha256": digest(data)})
    with zipfile.ZipFile(archive_path) as archive:
        assert set(archive.namelist()) == {item["path"] for item in inventory}
        for item in inventory:
            assert digest(archive.read(item["path"])) == item["sha256"], item["path"]
    archive_bytes = archive_path.stat().st_size
    archive_hash = digest(archive_path.read_bytes())
    parts = []
    combined_hash = hashlib.sha256()
    with archive_path.open("rb") as stream:
        index = 1
        while data := stream.read(80 * 1024 * 1024):
            part = history / f"{archive_path.name}.{index:03d}"
            with part.open("xb") as target:
                target.write(data)
            verified = part.read_bytes()
            assert digest(verified) == digest(data)
            combined_hash.update(verified)
            parts.append({"path": part.name, "bytes": len(verified), "sha256": digest(verified)})
            index += 1
    assert combined_hash.hexdigest() == archive_hash
    # Nur die selbst erzeugte, geprüfte Datei im eigenen Ausgabeordner entfernen.
    assert archive_path.resolve().parent == history.resolve()
    archive_path.unlink()
    audit = source / "40_EVIDENCE/CLIENT_V2_PLANUNG/2026-10-11_ERSTER_DURCHLAUF"
    original_manifest = json.loads((audit / "IMPORT_MANIFEST.json").read_text(encoding="utf-8-sig"))
    for item in original_manifest["files"]:
        assert digest((audit / item["path"]).read_bytes()) == item["sha256"], item["path"]
    copied = []
    for path in sorted(audit.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(audit)
        target = destination / relative
        if target.exists():
            raise SystemExit(f"Ein vorhandenes Importziel wird nicht überschrieben: {relative}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        assert digest(path.read_bytes()) == digest(target.read_bytes())
        copied.append(relative.as_posix())
    manifest = {
        "schemaVersion": 1,
        "date": "2026-10-11",
        "purpose": "Vollständige historische Sicherung des früheren Themenbestands; nicht normativ",
        "sourceOriginHistoricalOnly": str(source),
        "archive": archive_path.name,
        "archiveBytes": archive_bytes,
        "archiveSha256": archive_hash,
        "archiveParts": parts,
        "archiveReconstruction": "Concatenate archiveParts in listed order; verify archiveSha256 before opening ZIP",
        "sourceFiles": len(inventory),
        "sourceBytes": sum(item["bytes"] for item in inventory),
        "archiveEntriesAndEveryPayloadHashVerified": True,
        "expandedAuditFilesInitiallyByteIdentical": copied,
        "files": inventory,
    }
    inventory_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: manifest[key] for key in (
        "sourceFiles", "sourceBytes", "archiveBytes", "archiveSha256",
        "archiveEntriesAndEveryPayloadHashVerified", "expandedAuditFilesInitiallyByteIdentical"
    )}, ensure_ascii=False))


if __name__ == "__main__":
    main()
