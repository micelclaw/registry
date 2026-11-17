#!/usr/bin/env python3
"""Retain hash-checked upstream source bytes and deterministic release shards.

No sources are executed. Publication is a separate authorised operation.
"""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import re
import tarfile
import urllib.request


def digest_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def retain(entry, destination):
    if not re.fullmatch(r"[a-f0-9]{64}", entry["sha256"]):
        raise ValueError("Invalid source SHA-256")
    if not re.fullmatch(r"[A-Za-z0-9.+_~:-]+", entry["filename"]) or entry["filename"] in {".", ".."}:
        raise ValueError("Unsafe source filename")
    if type(entry["bytes"]) is not int or not 0 < entry["bytes"] <= 1024 ** 3:
        raise ValueError("Invalid source byte limit")
    if not re.fullmatch(r"https://snapshot\.debian\.org/file/[a-f0-9]{40}", entry["url"]):
        raise ValueError("Unexpected upstream source host")
    target = destination / entry["sha256"] / entry["filename"]
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size == entry["bytes"] and digest_file(target) == entry["sha256"]:
        return target
    partial = target.with_name(target.name + ".partial")
    try:
        digest = hashlib.sha256()
        count = 0
        with urllib.request.urlopen(entry["url"], timeout=90) as response, partial.open("xb") as output:
            if not response.geturl().startswith("https://snapshot.debian.org/"):
                raise ValueError("Unexpected source redirect")
            while block := response.read(1024 * 1024):
                count += len(block)
                if count > entry["bytes"]:
                    raise ValueError("Source byte limit exceeded")
                digest.update(block)
                output.write(block)
        if count != entry["bytes"] or digest.hexdigest() != entry["sha256"]:
            raise ValueError("Source integrity mismatch")
        partial.rename(target)
        return target
    finally:
        partial.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("index", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    data = json.loads(args.index.read_text())
    if data["errors"]:
        raise ValueError("Incomplete source inventory")
    entries = [entry for source in data["sources"] for entry in source["files"]]
    errors = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        jobs = {pool.submit(retain, entry, args.destination / "files"): entry for entry in entries}
        for future in concurrent.futures.as_completed(jobs):
            try:
                future.result()
            except Exception as error:
                entry = jobs[future]
                errors.append({"filename": entry["filename"], "error_type": type(error).__name__})
    if errors:
        print(json.dumps({"errors": errors}))
        raise SystemExit(1)
    shards = []
    current = []
    size = 0
    for entry in sorted(entries, key=lambda e: (e["filename"], e["sha256"])):
        if entry["bytes"] > 1024 ** 3:
            raise ValueError("A source archive exceeds shard limit")
        padded = ((entry["bytes"] + 511) // 512 + 4) * 512
        if current and size + padded > 1024 ** 3:
            shards.append(current)
            current, size = [], 0
        current.append(entry)
        size += padded
    if current:
        shards.append(current)
    outputs = []
    for number, shard_entries in enumerate(shards, 1):
        filename = f"office-0.2.0-debian-sources-{number:02d}.tar"
        target = args.destination / filename
        if target.exists():
            raise ValueError("Refusing to overwrite a source shard")
        with tarfile.open(target, "w", format=tarfile.PAX_FORMAT) as archive:
            for entry in shard_entries:
                local = args.destination / "files" / entry["sha256"] / entry["filename"]
                arcname = "sources/" + entry["sha256"] + "/" + entry["filename"]
                info = tarfile.TarInfo(arcname)
                info.size, info.mode, info.mtime = entry["bytes"], 0o644, 0
                with local.open("rb") as stream:
                    archive.addfile(info, stream)
                entry["retained_path"] = arcname
                entry["release_asset"] = filename
                entry["archive_bytes_verified"] = True
        outputs.append({"filename": filename, "bytes": target.stat().st_size, "sha256": digest_file(target)})
    for source in data["sources"]:
        source["source_archive_bytes_verified"] = True
    data["source_shards"] = outputs
    data["verification_scope"] = "All Debian source descriptor/archive bytes match exact recorded SHA-256 and byte length; retained locally in deterministic shards. Public availability must be verified separately."
    (args.destination / "retained-source-index.json").write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps({"verified_files": len(entries), "source_shards": outputs}))


if __name__ == "__main__":
    main()
