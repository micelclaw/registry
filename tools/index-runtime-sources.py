#!/usr/bin/env python3
"""Index exact Debian source versions without downloading or executing binaries.

The index verifies .dsc bytes and records their SHA-256 file checksums. It is
not a substitute for supplying/retaining corresponding source archives.
"""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import re
import time
import urllib.parse
import urllib.request

BASE = "https://snapshot.debian.org"


def fetch(url, limit=2 * 1024 * 1024):
    if not url.startswith(BASE + "/"):
        raise ValueError("Unexpected source host")
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "micelclaw-source-review/1"})
            with urllib.request.urlopen(req, timeout=30) as response:
                if not response.geturl().startswith(BASE + "/"):
                    raise ValueError("Unexpected redirect")
                body = response.read(limit + 1)
            if len(body) > limit:
                raise ValueError("Metadata limit exceeded")
            return body
        except (OSError, ValueError):
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def package(name, version, cache):
    key = hashlib.sha256((name + "\n" + version).encode()).hexdigest()
    cached = cache / (key + ".json")
    if cached.exists():
        result = json.loads(cached.read_text())
        if result["name"] == name and result["version"] == version:
            return result
    api = BASE + "/mr/package/" + urllib.parse.quote(name, safe="") + "/" + urllib.parse.quote(version, safe="") + "/srcfiles"
    data = json.loads(fetch(api))
    if data["package"] != name or data["version"] != version:
        raise ValueError("Source package mismatch")
    files = []
    candidates = []
    dsc = None
    dsc_filename = name + "_" + version.split(":", 1)[-1] + ".dsc"
    for item in data["result"]:
        sha1 = item["hash"]
        if not re.fullmatch(r"[a-f0-9]{40}", sha1):
            raise ValueError("Invalid Snapshot hash")
        info = json.loads(fetch(BASE + "/mr/file/" + sha1 + "/info"))
        variants = {(v["name"], v["size"]) for v in info["result"]}
        for filename, size in sorted(variants):
            if not re.fullmatch(r"[A-Za-z0-9.+_~:-]+", filename):
                raise ValueError("Unsafe source filename")
            entry = {"filename": filename, "bytes": size, "snapshot_sha1": sha1, "url": BASE + "/file/" + sha1}
            candidates.append(entry)
            if filename == dsc_filename:
                body = fetch(entry["url"])
                if len(body) != size or hashlib.sha1(body).hexdigest() != sha1:
                    raise ValueError("Descriptor integrity mismatch")
                entry["sha256"] = hashlib.sha256(body).hexdigest()
                files.append(entry)
                dsc = body.decode("utf-8")
                (cache / filename).write_bytes(body)
    if dsc is None or not re.search(r"^Source: " + re.escape(name) + r"$", dsc, re.M) or not re.search(r"^Version: " + re.escape(version) + r"$", dsc, re.M):
        raise ValueError("Source descriptor mismatch")
    section = re.search(r"^Checksums-Sha256:\n((?:[ \t].*\n)+)", dsc, re.M)
    if not section:
        raise ValueError("Missing strong source checksums")
    checksums = {}
    for line in section[1].splitlines():
        digest, size, filename = line.split()
        if not re.fullmatch(r"[a-f0-9]{64}", digest):
            raise ValueError("Invalid SHA-256")
        checksums[filename] = (digest, int(size))
    for entry in candidates:
        match = checksums.get(entry["filename"])
        if match is None:
            continue  # Snapshot content hashes can have aliases in other packages.
        digest, size = match
        if size != entry["bytes"]:
            raise ValueError("Source size mismatch")
        entry["sha256"] = digest
        files.append(entry)
        del checksums[entry["filename"]]
    if checksums:
        raise ValueError("Snapshot omitted descriptor source files")
    result = {"name": name, "version": version, "metadata_url": api, "descriptor_bytes_verified": True, "source_archive_bytes_verified": False, "files": sorted(files, key=lambda f: f["filename"])}
    cached.write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notices", type=Path)
    parser.add_argument("cache", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    inventories = {name: json.loads((args.notices / name / "manifest.json").read_text()) for name in ["documents", "spreadsheets", "presentations", "pdf"]}
    versions = sorted({(p["source"], p["source_version"]) for inv in inventories.values() for p in inv["packages"]})
    result = {"schema_version": 1, "verification_scope": "Exact source-package metadata and descriptor integrity; archive bytes not downloaded by this indexer. No retention guarantee inferred from third-party links.", "images": [{"name": name, "image": inv["image"], "packages": inv["packages"]} for name, inv in inventories.items()], "sources": [], "errors": []}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        jobs = {pool.submit(package, name, version, args.cache): (name, version) for name, version in versions}
        for future in concurrent.futures.as_completed(jobs):
            try:
                result["sources"].append(future.result())
            except Exception as error:
                name, version = jobs[future]
                result["errors"].append({"name": name, "version": version, "error_type": type(error).__name__})
    result["sources"].sort(key=lambda item: (item["name"], item["version"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    total = sum(f["bytes"] for s in result["sources"] for f in s["files"])
    print(json.dumps({"source_packages": len(result["sources"]), "errors": result["errors"], "archive_bytes_to_supply": total}))
    raise SystemExit(bool(result["errors"]))


if __name__ == "__main__":
    main()
