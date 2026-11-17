#!/usr/bin/env python3
"""Local publisher. Password input stays in stdin; Docker auth is temporary.

Run only after the reviewed release preparation has produced images.json.
No Core/Drive/service start, registry installation or runtime configuration.
"""
import argparse
import getpass
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request
import urllib.error
import warnings


def run(args, **kwargs):
    result = subprocess.run(args, **kwargs)
    if result.returncode:
        raise SystemExit(f"Command failed: {args[0]} (exit {result.returncode}).")
    return result


def public_manifest(image, digest):
    repository = image.removeprefix("ghcr.io/")
    url = "https://ghcr.io/token?service=ghcr.io&scope=repository:" + repository + ":pull"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            token = json.load(response)["token"]
        request = urllib.request.Request(
            f"https://ghcr.io/v2/{repository}/manifests/{digest}",
            headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.docker.distribution.manifest.v2+json, application/vnd.oci.image.manifest.v1+json"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read(4 * 1024 * 1024)
            return "sha256:" + hashlib.sha256(payload).hexdigest() == digest
    except (urllib.error.URLError, KeyError):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("preparation", type=Path)
    args = parser.parse_args()
    preparation = json.loads(args.preparation.read_text())
    if preparation.get("schema_version") != 1 or preparation.get("registry") != "https://github.com/micelclaw/registry":
        raise SystemExit("Invalid reviewed release preparation.")
    images = preparation["images"]
    expected = {"documents", "spreadsheets", "presentations", "pdf"}
    if {image["app"] for image in images} != expected or len(images) != 4:
        raise SystemExit("Exactly the four approved Office images are required.")
    for image in images:
        if image["repository"] != "ghcr.io/micelclaw/office-" + image["app"] or image["tag"] != "0.2.0":
            raise SystemExit("Unexpected publication destination.")
        info = run(["docker", "image", "inspect", "--format", "{{.Id}}", image["local_id"]], capture_output=True, text=True).stdout.strip()
        if info != image["local_id"]:
            raise SystemExit("Reviewed image changed.")
    print("Publishes ONLY the four reviewed Office images. No installation or Core restart.")
    print("Provide a GitHub classic PAT with write:packages and organisation access in this LOCAL prompt.")
    print("Do not paste credentials in chat. Temporary Docker credentials are removed when this command exits.")
    if not sys.stdin.isatty() or not sys.stderr.isatty():
        raise SystemExit("Run in a real local terminal; refusing non-interactive password input.")
    warnings.simplefilter("error", getpass.GetPassWarning)
    secret = getpass.getpass("GHCR publishing credential (hidden): ")
    if not secret:
        raise SystemExit("No credential supplied; nothing published.")
    base = Path("/run/user") / str(os.getuid())
    if not base.is_dir():
        raise SystemExit("Private runtime directory is unavailable; no credential stored.")
    results = []
    with tempfile.TemporaryDirectory(prefix="micelclaw-registry-publish-", dir=base) as temp:
        os.chmod(temp, 0o700)
        command = ["docker", "--config", temp]
        login = subprocess.run(command + ["login", "ghcr.io", "--username", preparation["publisher"], "--password-stdin"], input=secret + "\n", text=True, capture_output=True)
        del secret
        if login.returncode:
            raise SystemExit("GHCR login failed; credential details are not printed.")
        try:
            existing = {}
            # Complete all collision checks before the first publication.
            for image in images:
                target = image["repository"] + ":" + image["tag"]
                check = subprocess.run(command + ["manifest", "inspect", "--verbose", target], capture_output=True, text=True)
                if check.returncode == 0:
                    manifest = json.loads(check.stdout)
                    config = manifest.get("SchemaV2Manifest", {}).get("config", {}).get("digest")
                    if config != image["local_id"]:
                        raise SystemExit("A different release already exists; refusing overwrite: " + target)
                    existing[image["app"]] = manifest["Descriptor"]["digest"]
                elif not any(reason in check.stderr.lower() for reason in ["manifest unknown", "no such manifest"]):
                    raise SystemExit("Could not prove absence of release tag; no image published: " + target)
            for image in images:
                target = image["repository"] + ":" + image["tag"]
                if image["app"] in existing:
                    pinned = image["repository"] + "@" + existing[image["app"]]
                else:
                    run(command + ["tag", image["local_id"], target])
                    run(command + ["push", target])
                    inspected = run(command + ["image", "inspect", "--format", "{{json .RepoDigests}}", target], capture_output=True, text=True)
                    matches = [value for value in json.loads(inspected.stdout) if value.startswith(image["repository"] + "@sha256:")]
                    if len(matches) != 1:
                        raise SystemExit("Registry digest could not be confirmed.")
                    pinned = matches[0]
                results.append({"app": image["app"], "image": pinned, "local_id": image["local_id"], "anonymous_manifest": public_manifest(image["repository"], pinned.split("@", 1)[1])})
                result_path = args.preparation.with_name("published-images.json")
                result_path.write_text(json.dumps({"schema_version": 1, "complete": False, "images": results}, indent=2) + "\n")
                # A GitHub package is initially private even if its linked repository is public.
                if not results[-1]["anonymous_manifest"]:
                    print("Set PUBLIC visibility in the official package settings (no token in the URL):")
                    print("https://github.com/orgs/micelclaw/packages/container/office-" + image["app"] + "/settings")
            if any(not result["anonymous_manifest"] for result in results):
                input("Set the four package visibilities to PUBLIC in GitHub, then press Enter here: ")
                for result in results:
                    image, digest = result["image"].split("@", 1)
                    result["anonymous_manifest"] = public_manifest(image, digest)
            complete = len(results) == 4 and all(result["anonymous_manifest"] for result in results)
            result_path.write_text(json.dumps({"schema_version": 1, "complete": complete, "images": results}, indent=2) + "\n")
            if not complete:
                raise SystemExit("Publication incomplete: anonymous digest retrieval failed. Do not install these packages.")
            print("Four image digests recorded; anonymous manifest retrieval verified. No apps installed.")
        finally:
            subprocess.run(command + ["logout", "ghcr.io"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
