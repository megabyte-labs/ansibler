# @pythonBrew [ansibler](https://github.com/megabyte-labs/ansibler) - An Ansible CLI tool that generates platform compatibility data and charts from Molecule test results
Creating virtualenv ansibler-jA275Cdz-py3.9 in /home/megabyte/.cache/pypoetry/virtualenvs
class Ansibler < Formula
  include Language::Python::Virtualenv

  desc "Shiny new formula"
  homepage "https://gitlab.com/megabyte-labs/python/ansibler/"
  url "https://files.pythonhosted.org/packages/bd/e1/a7e500b91f614b3b0a030f7d1d29907c94e63ed419afacdb2242a6bc59ba/ansibler-0.3.1.tar.gz"
  sha256 "85098d9153f8552d287c428169e1c3a4db45243f6ecd08e1b5a90812b42477fa"

  depends_on "python3"

  def install
    virtualenv_create(libexec, "python3")
    virtualenv_install_with_resources
  end

  test do
    false
  end
end

