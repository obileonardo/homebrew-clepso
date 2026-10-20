cask "clepso" do
  version "0.2.0-alpha.5"
  sha256 "5b742de8139c5afc79d9776e40391ad6a499d926c743f65de31fd8db4e461d5b"

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
