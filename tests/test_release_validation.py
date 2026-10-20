import copy
import hashlib
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("updater", Path(__file__).resolve().parents[1] / "scripts/update-cask.py")
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class ReleaseValidation(unittest.TestCase):
    def setUp(self):
        self.version = "0.2.0-alpha.5"
        self.filename = f"Clepso-{self.version}.dmg"
        self.payload = b"fixture disk image"
        self.digest = hashlib.sha256(self.payload).hexdigest()
        self.release = {"tag_name": f"v{self.version}", "draft": False, "prerelease": False,
                        "published_at": "2026-10-20T15:45:15Z", "assets": []}
        for name in (self.filename, "SHA256SUMS"):
            self.release["assets"].append({"name": name, "state": "uploaded", "size": len(self.payload),
                "digest": f"sha256:{self.digest}",
                "browser_download_url": f"https://github.com/{updater.REPO}/releases/download/v{self.version}/{name}"})

    def test_public_release_and_valid_manifest(self):
        version, assets = updater.release_assets(self.release)
        self.assertEqual(version, self.version)
        self.assertEqual(updater.validate_download(assets[self.filename], self.payload), self.digest)
        for marker in (" ", "*"):
            updater.verify_manifest(f"{self.digest} {marker}{self.filename}\n".encode(), self.filename, self.digest)

    def test_reject_draft_or_unpublished(self):
        for field, value in (("draft", True), ("prerelease", True), ("published_at", None)):
            with self.subTest(field=field), self.assertRaises(ValueError):
                updater.release_assets(dict(self.release, **{field: value}))

    def test_reject_metadata_injection_and_unexpected_tags(self):
        for tag in ('v0.2.0";system("bad")', "main", "v0.2", "v0.2.0-alpha/5"):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                updater.release_assets(dict(self.release, tag_name=tag))

    def test_reject_replaced_asset_origin_size_or_digest(self):
        for field, value in (("browser_download_url", "https://example.org/replaced.dmg"),
                             ("state", "new"), ("size", 0), ("size", 101 * 1024 * 1024),
                             ("digest", None), ("digest", "sha256:bad")):
            release = copy.deepcopy(self.release)
            release["assets"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                updater.release_assets(release)

    def test_reject_missing_and_duplicate_assets(self):
        for assets in ([], self.release["assets"] + [self.release["assets"][0]]):
            with self.subTest(assets=assets), self.assertRaises(ValueError):
                updater.release_assets(dict(self.release, assets=assets))

    def test_reject_changed_or_truncated_download(self):
        for payload in (b"modified disk image", self.payload[:-1]):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                updater.validate_download(self.release["assets"][0], payload)

    def test_reject_wrong_missing_or_duplicate_manifest_entry(self):
        valid = f"{self.digest}  {self.filename}\n".encode()
        for payload in (b"", valid.replace(self.filename.encode(), b"other.dmg"), valid + valid,
                        valid.replace(self.digest.encode(), b"0" * 64)):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                updater.verify_manifest(payload, self.filename, self.digest)

    def test_fixed_template_and_stable_future_version(self):
        release = copy.deepcopy(self.release)
        release["tag_name"] = "v0.3.0"
        for asset in release["assets"]:
            asset["name"] = asset["name"].replace(self.version, "0.3.0")
            asset["browser_download_url"] = asset["browser_download_url"].replace(self.version, "0.3.0")
        self.assertEqual(updater.release_assets(release)[0], "0.3.0")
        text = 'cask "clepso" do\n  version "0.1.0"\n  sha256 "' + '0' * 64 + '"\nend\n'
        result = updater.update_text(text, self.version, self.digest)
        self.assertIn(f'  version "{self.version}"', result)
        self.assertIn(self.digest, result)
        for broken in ("", text + text):
            with self.assertRaises(ValueError):
                updater.update_text(broken, self.version, self.digest)


if __name__ == "__main__":
    unittest.main()
