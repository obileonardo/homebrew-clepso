cask "clepso" do
  version "0.3.0-alpha.3"
  sha256 "e34982f0a34c48694aa0da5ba77ecf883efb78b421753e59d8c740e6eab596fd"

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
