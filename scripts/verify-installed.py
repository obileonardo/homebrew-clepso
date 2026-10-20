#!/usr/bin/env python3
"""Verify the cask-installed bundle without launching it or touching user data."""

from pathlib import Path
import plistlib
import re
import subprocess
import sys

app = Path(sys.argv[1]).resolve(strict=True)
text = (Path(__file__).resolve().parents[1] / "Casks/clepso.rb").read_text()
version = re.search(r'^  version "([^"]+)"$', text, re.MULTILINE)[1]
with (app / "Contents/Info.plist").open("rb") as stream:
    info = plistlib.load(stream)
if info["CFBundleIdentifier"] != "com.elvisobi.clepso":
    sys.exit("Unexpected bundle identifier")
if info["CFBundleShortVersionString"] != version.split("-")[0]:
    sys.exit("Bundle version differs from cask")
subprocess.run(["codesign", "--verify", "--deep", "--strict", str(app)], check=True)
signature = subprocess.run(["codesign", "-dv", "--verbose=4", str(app)], check=True, capture_output=True, text=True).stderr
if "TeamIdentifier=DD8UY75RZT" not in signature or "Authority=Developer ID Application:" not in signature:
    sys.exit("Unexpected Developer ID signer")
subprocess.run(["spctl", "--assess", "--type", "execute", "--verbose=2", str(app)], check=True)
print(f"Verified Clepso {version}, build {info['CFBundleVersion']}, Developer ID DD8UY75RZT; Gatekeeper accepted")
