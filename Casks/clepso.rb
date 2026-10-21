cask "clepso" do
  version "0.3.0-alpha.2"
  sha256 "3c54cc086e00607fe076b1059c786de105df4a512aca6b75213d598c40eeb2aa"

  url "https://github.com/obileonardo/clepso/releases/download/v#{version}/Clepso-#{version}.dmg"
  name "Clepso"
  desc "Menu bar usage monitor for Claude Code and Codex"
  homepage "https://github.com/obileonardo/clepso"

  livecheck do
    url :url
    regex(/^v?(\d+\.\d+\.\d+(?:-(?:alpha|beta|rc)\.\d+)?)$/i)
    strategy :github_latest
  end

  depends_on arch: :arm64
  depends_on macos: :sonoma

  app "Clepso.app"
end
