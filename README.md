# Clepso Homebrew tap

Install [Clepso](https://github.com/obileonardo/clepso), a local-first macOS menu bar usage monitor for Claude Code and Codex.

The current release is an **alpha** for **Apple silicon and macOS 14 Sonoma or later**. The cask installs the same Developer ID signed, notarized and stapled app as the public GitHub DMG. Intel and Linux are not supported by this binary.

## Install

With [Homebrew](https://brew.sh) installed:

```sh
brew install --cask obileonardo/clepso/clepso
open -a Clepso
```

Homebrew adds this tap automatically. If your Homebrew version asks you to trust third-party casks, review [Casks/clepso.rb](Casks/clepso.rb) and approve this cask. For a noninteractive setup on versions that support `brew trust`:

```sh
brew tap obileonardo/clepso
brew trust --cask obileonardo/clepso/clepso
brew install --cask --require-sha obileonardo/clepso/clepso
```

Open Clepso to complete setup. Homebrew does not connect agents, enable file reading, grant macOS permissions or change your settings.

## Existing DMG installation

Quit Clepso first. If the existing app is the **same release**, adopt it instead of installing a second copy:

```sh
# App currently in /Applications:
brew install --cask --adopt obileonardo/clepso/clepso

# Or, app currently in your personal Applications folder:
brew install --cask --adopt --appdir="$HOME/Applications" obileonardo/clepso/clepso
```

`--adopt` requires identical app contents and refuses a mismatch. If your app is older, back up your data, quit Clepso and move the old app out of the destination before installing the cask. Keep your Library data; do not use `--force` to bypass a mismatch. Use a single app copy, then reopen it. If you change its location, reconnect Claude Code from Clepso Settings so its helper path points to the installed app.

## Update

Quit Clepso, then:

```sh
brew update
brew upgrade --cask --greedy obileonardo/clepso/clepso
open -a Clepso
```

Homebrew upgrades to the release pinned in the tap. From 0.4.0 alpha 1, Clepso also offers signed in-app updates in Settings.
Automatic checks and installation start off; enable them if you prefer that route. The cask declares `auto_updates true`,
so use `--greedy` when requesting a Homebrew upgrade. User data and settings remain in your Library.

The cask links the signed `clepso` CLI from the app. To use its read-only MCP server, first allow a named client in
Clepso Settings → Integrations, review the disclosure and copy setup. The server does not change client configuration.

## Uninstall

In Clepso Settings, remove the Claude Code connection and disable launch at login if enabled. Quit the app, then:

```sh
brew uninstall --cask obileonardo/clepso/clepso
```

This cask removes the app and preserves usage history and preferences. It has no `zap` stanza and does not edit agent configuration or delete user data.

## Release maintenance

After publishing the next Clepso release as GitHub **Latest**, work in the actual tapped checkout so Homebrew audits your edited cask:

```sh
cd "$(brew --repository obileonardo/clepso)"
git switch -c update/clepso-release
python3 scripts/update-cask.py
brew style Casks/clepso.rb
brew audit --cask --strict --online obileonardo/clepso/clepso
git diff
# Commit and push the reviewed version/checksum change, then open a pull request.
```

The updater only accepts public Latest releases from `obileonardo/clepso`. It validates the tag, asset URLs and sizes, downloads the DMG and `SHA256SUMS`, and requires their computed SHA-256 values to agree with GitHub's asset digests and the checksum manifest. It never executes release metadata as code. `python3 scripts/update-cask.py --check` checks without writing files.

CI checks syntax, updater validation and Homebrew style/audit, then installs and uninstalls the cask in a temporary app directory on an Apple silicon Mac. It verifies the bundle version, Developer ID team and Gatekeeper acceptance. The release monitor checks daily for an unreflected Latest release; it reports a failed check rather than publishing an unreviewed cask change. No extra credentials or server are required.

Homebrew reference: [third-party taps](https://docs.brew.sh/How-to-Create-and-Maintain-a-Tap), [Cask Cookbook](https://docs.brew.sh/Cask-Cookbook).
