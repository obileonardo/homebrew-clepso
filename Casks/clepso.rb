cask "clepso" do
  version "0.4.0-alpha.2"
  sha256 "81454a3f57eb10644500b10333da2e8bca67982b6e2ef523f3a543c39fba0fa9"

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
