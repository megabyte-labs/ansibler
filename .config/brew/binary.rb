# @binaryBrew [Ansibler](https://github.com/megabyte-labs/ansibler) - An Ansible CLI tool that generates platform compatibility data and charts from Molecule test results
class Ansibler < Formula
  desc "An Ansible CLI tool that generates platform compatibility data and charts from Molecule test results"
  homepage "https://megabyte.space"
  url "https://github.com/megabyte-labs/ansibler/releases/download/v0.2.4/ansibler.tar.gz"
  version "0.2.4"
  license "MIT"

  

  def install
    os = OS.kernel_name.downcase
    arch = Hardware::CPU.intel? ? "amd64" : Hardware::CPU.arch.to_s
    bin.install "build/ansibler-#{os}_#{arch}" => "ansibler"
  done

  test do
    system bin/"ansibler", "--version"
  end
end
