#!/usr/bin/env python3
"""Pin the official public Latest release after validating its downloaded assets."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import urllib.request

REPO = "obileonardo/clepso"
API = f"https://api.github.com/repos/{REPO}/releases/latest"
VERSION = r"\d+\.\d+\.\d+(?:-(?:alpha|beta|rc)\.\d+)?"
CASK = Path(__file__).resolve().parents[1] / "Casks" / "clepso.rb"


def download(url, limit, *, api=False):
    headers = {"User-Agent": "clepso-tap-updater", "Accept": "application/vnd.github+json" if api else "application/octet-stream"}
    if api and os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("Download exceeded its size limit")
    return data


def release_assets(release):
    if release.get("draft") is not False or release.get("prerelease") is not False or not release.get("published_at"):
        raise ValueError("Expected a published, non-draft GitHub Latest release")
    tag = release.get("tag_name", "")
    if not re.fullmatch(f"v({VERSION})", tag):
        raise ValueError("Unexpected release tag")
    version = tag[1:]
    prefix = f"https://github.com/{REPO}/releases/download/{tag}/"
    selected = {}
    for name in (f"Clepso-{version}.dmg", "SHA256SUMS"):
        matches = [a for a in release.get("assets", []) if a.get("name") == name]
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one asset: {name}")
        asset = matches[0]
        maximum = 100 * 1024 * 1024 if name.endswith(".dmg") else 64 * 1024
        if asset.get("state") != "uploaded" or asset.get("browser_download_url") != prefix + name:
            raise ValueError(f"Unexpected asset location/state: {name}")
        if type(asset.get("size")) is not int or not 0 < asset["size"] <= maximum:
            raise ValueError(f"Unexpected asset size: {name}")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", asset.get("digest") or ""):
            raise ValueError(f"Missing SHA-256 asset digest: {name}")
        selected[name] = asset
    return version, selected


def validate_download(asset, payload):
    checksum = hashlib.sha256(payload).hexdigest()
    if len(payload) != asset["size"] or f"sha256:{checksum}" != asset["digest"]:
        raise ValueError(f"Asset size/digest mismatch: {asset['name']}")
    return checksum


def verify_manifest(payload, filename, expected):
    entries = []
    for line in payload.decode("utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64}) [ *](.+)", line)
        if match and match[2] == filename:
            entries.append(match[1])
    if entries != [expected]:
        raise ValueError("SHA256SUMS must contain one matching DMG checksum")


def update_text(text, version, checksum):
    # Fixed template: release metadata can only replace a version and a hex digest.
    for pattern, replacement in (
        (rf'^  version "{VERSION}"$', f'  version "{version}"'),
        (r'^  sha256 "[0-9a-f]{64}"$', f'  sha256 "{checksum}"'),
    ):
        text, count = re.subn(pattern, lambda _: replacement, text, flags=re.MULTILINE)
        if count != 1:
            raise ValueError("Cask template changed; review it manually")
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the cask is behind Latest; never write")
    args = parser.parse_args()
    release = json.loads(download(API, 1024 * 1024, api=True))
    version, assets = release_assets(release)
    downloaded = {}
    hashes = {}
    for name, asset in assets.items():
        downloaded[name] = download(asset["browser_download_url"], asset["size"])
        hashes[name] = validate_download(asset, downloaded[name])
    filename = f"Clepso-{version}.dmg"
    verify_manifest(downloaded["SHA256SUMS"], filename, hashes[filename])
    old = CASK.read_text()
    new = update_text(old, version, hashes[filename])
    if old == new:
        print(f"Clepso {version}: cask and downloaded release checksums agree")
    elif args.check:
        raise ValueError(f"Cask differs from public Latest ({version}); run scripts/update-cask.py and review the diff")
    else:
        CASK.write_text(new)
        print(f"Pinned Clepso {version}; review and commit Casks/clepso.rb")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        sys.exit(f"Update refused: {error}")
