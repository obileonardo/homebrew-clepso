cask "clepso" do
  version "0.4.0-alpha.1"
  sha256 "c6d2cc8d57126180da6c8976250a6bde9b914e3b873c4272f53973dacdae66e1"

  url "https://github.com/obileonardo/clepso/releases/download/v#{version}/Clepso-#{version}.dmg"
  name "Clepso"
  desc "Menu bar usage monitor for Claude Code and Codex"
  homepage "https://github.com/obileonardo/clepso"

  livecheck do
    url :url
    regex(/^v?(\d+\.\d+\.\d+(?:-(?:alpha|beta|rc)\.\d+)?)$/i)
    strategy :github_latest
  end

  auto_updates true
  depends_on arch: :arm64
  depends_on macos: :sonoma

  app "Clepso.app"
  binary "#{appdir}/Clepso.app/Contents/Helpers/clepso"
end
