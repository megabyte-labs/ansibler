<!-- ⚠️ This README has been generated from the file(s) ".config/docs/blueprint-readme-cli.md" ⚠️--><div align="center">
  <center>
    <a href="https://github.com/ProfessorManhattan/ansibler">
      <img width="148" height="148" alt="Ansibler logo" src="https://gitlab.com/megabyte-labs/python/cli/ansibler/-/raw/master/logo.png" />
    </a>
  </center>
</div>
<div align="center">
  <center><h1 align="center">Python CLI: Ansibler - Compatibility Data Tool for Ansible<i></i></h1></center>
  <center><h4 style="color: #18c3d1;">A Python CLI created by <a href="https://megabyte.space" target="_blank">Megabyte Labs</a></h4><i></i></center>
</div>

<div align="center">
  <a href="https://megabyte.space" title="Megabyte Labs homepage" target="_blank">
    <img alt="Homepage" src="https://img.shields.io/website?down_color=%23FF4136&down_message=Down&label=Homepage&logo=home-assistant&logoColor=white&up_color=%232ECC40&up_message=Up&url=https%3A%2F%2Fmegabyte.space&style=for-the-badge" />
  </a>
  <a href="https://github.com/ProfessorManhattan/ansibler/blob/master/docs/CONTRIBUTING.md" title="Learn about contributing" target="_blank">
    <img alt="Contributing" src="https://img.shields.io/badge/Contributing-Guide-0074D9?logo=github-sponsors&logoColor=white&style=for-the-badge" />
  </a>
  <a href="https://app.slack.com/client/T01ABCG4NK1/C01NN74H0LW/details/" title="Chat with us on Slack" target="_blank">
    <img alt="Slack" src="https://img.shields.io/badge/Slack-Chat-e01e5a?logo=slack&logoColor=white&style=for-the-badge" />
  </a>
  <a href="https://github.com/ProfessorManhattan/ansibler" title="GitHub mirror" target="_blank">
    <img alt="GitHub" src="https://img.shields.io/badge/Mirror-GitHub-333333?logo=github&style=for-the-badge" />
  </a>
  <a href="https://gitlab.com/megabyte-labs/python/cli/ansibler" title="GitLab repository" target="_blank">
    <img alt="GitLab" src="https://img.shields.io/badge/Repo-GitLab-fc6d26?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgAQMAAABJtOi3AAAABlBMVEUAAAD///+l2Z/dAAAAAXRSTlMAQObYZgAAAHJJREFUCNdNxKENwzAQQNEfWU1ZPUF1cxR5lYxQqQMkLEsUdIxCM7PMkMgLGB6wopxkYvAeI0xdHkqXgCLL0Beiqy2CmUIdeYs+WioqVF9C6/RlZvblRNZD8etRuKe843KKkBPw2azX13r+rdvPctEaFi4NVzAN2FhJMQAAAABJRU5ErkJggg==&style=for-the-badge" />
  </a>
</div>
<br/>
<div align="center">
  <a title="Version: 0.0.1" href="https://github.com/ProfessorManhattan/ansibler" target="_blank">
    <img alt="Version: 0.0.1" src="https://img.shields.io/badge/version-0.0.1-blue.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgAQMAAABJtOi3AAAABlBMVEUAAAD///+l2Z/dAAAAAXRSTlMAQObYZgAAACNJREFUCNdjIACY//+BEp9hhM3hAzYQwoBIAqEDYQrCZLwAAGlFKxU1nF9cAAAAAElFTkSuQmCC&cacheSeconds=2592000&style=flat-square" />
  </a>
  <a title="Build status on GitLab" href="https://gitlab.com/megabyte-labs/python/cli/ansibler/-/commits/master" target="_blank">
    <img alt="GitLab build status" src="https://img.shields.io/gitlab/pipeline-status/megabyte-labs/python/cli/ansibler?branch=master&label=build&logo=gitlab&style=flat-square">
  </a>
  <a title="Test coverage report" href="https://gitlab.com/megabyte-labs/python/cli/ansibler/-/commits/master" target="_blank">
    <img alt="Coverage status" src="https://img.shields.io/gitlab/coverage/megabyte-labs/python/cli/ansibler/master/?label=coverage&logo=pytest&style=flat-square">
  </a>
  <a title="Documentation" href="https://megabyte.space/docs/python" target="_blank">
    <img alt="Documentation" src="https://img.shields.io/badge/documentation-yes-brightgreen.svg?logo=readthedocs&style=flat-square" />
  </a>
  <a title="Supported Python versions" href="https://pypi.org/project/{{(if customPyPiPackageName customPyPiPackageName (append repository.prefix.github slug))}}/" target="_blank">
    <img alt="Python versions" src="https://img.shields.io/pypi/pyversions/{{(if customPyPiPackageName customPyPiPackageName (append repository.prefix.github slug))}}/?label=python&logo=python&style=flat-square">
  </a>
  <a title="PyPi status" href="https://pypi.org/project/{{(if customPyPiPackageName customPyPiPackageName (append repository.prefix.github slug))}}/" target="_blank">
    <img alt="Status" src="https://img.shields.io/pypi/status/{{(if customPyPiPackageName customPyPiPackageName (append repository.prefix.github slug))}}/?label=status&logo=pypi&style=flat-square">
  </a>
  <a title="License: MIT" href="https://github.com/ProfessorManhattan/ansibler/blob/master/LICENSE" target="_blank">
    <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-yellow.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgAQMAAABJtOi3AAAABlBMVEUAAAD///+l2Z/dAAAAAXRSTlMAQObYZgAAAHpJREFUCNdjYOD/wMDAUP+PgYHxhzwDA/MB5gMM7AwMDxj4GBgKGGQYGCyAEEgbMDDwAAWAwmk8958xpIOI5zKH2RmOyhxmZjguAiKmgIgtQOIYmFgCIp4AlaQ9OczGkJYCJEAGgI0CGwo2HmwR2Eqw5SBnNIAdBHYaAJb6KLM15W/CAAAAAElFTkSuQmCC&style=flat-square" />
  </a>
</div>

> </br><h4 align="center">**Generate JSON data that describes the dependencies of an Ansible playbook/role. Also, automatically generate OS compatibility charts using Molecule.**</h4></br>

<!--TERMINALIZE![terminalizer_title](repository.group.python_cli/ansibler* **github**: /raw/master/docs/demo.gif
* **gitlab**: /-/raw/master/docs/demo.gif)TERMINALIZE-->

<a href="#table-of-contents" style="width:100%"><img style="width:100%" src="https://gitlab.com/megabyte-labs/assets/-/raw/master/png/aqua-divider.png" /></a>

## Table of Contents

- [Overview](#overview)
- [Usage](#usage)
  - [Generating Compatibility Charts](#generating-compatibility-charts)
  - [Populating Platforms](#populating-platforms)
  - [Role Dependency Charts](#role-dependency-charts)
- [Additional Info](#additional-info)
  - [Caching](#caching)
  - [Overriding ansibler.json and meta/main.yml](#overriding-ansiblerjson-and-metamainyml)
  - [Help](#help)
- [Installation](#installation)
  - [PyPi](#pypi)
  - [Install Doctor](#install-doctor)
  - [Homebrew](#homebrew)
  - [Chocolatey](#chocolatey)
  - [Binary Releases](#binary-releases)
- [Requirements](#requirements)
- [Contributing](#contributing)
- [License](#license)

<a href="#overview" style="width:100%"><img style="width:100%" src="https://gitlab.com/megabyte-labs/assets/-/raw/master/png/aqua-divider.png" /></a>

## Overview

**Ansibler** is a CLI tool meant to accompany Ansible project's that wish to convey accurate information to the public. In an Ansibler workflow, instead of marking every platform as `all` in `meta/main.yml`, we first run Molecule tests and save the logs. Ansibler can take the logs and do a few cool things with them. It generates compatibility chart data in JSON format that you can embed in the `README.md` with [@appnest/readme](https://www.npmjs.com/package/@appnest/readme). After that, you can use Ansibler to automatically generate **accurate** `meta/main.yml` platform data.

<a href="#usage" style="width:100%"><img style="width:100%" src="https://gitlab.com/megabyte-labs/assets/-/raw/master/png/aqua-divider.png" /></a>

## Usage

With Ansibler, you can extract both role dependencies and OS compatibility data with the help of [Molecule Tests](https://molecule.readthedocs.io/en/latest/).

### Generating Compatibility Charts

Say you have run `molecule test` and want to generate updated compatibility charts for your role using the test's output. With Ansibler, it's possible to do just that!

1. Start by dumping the results of your test to `./.molecule-results/YEAR-MONTH-DAY-scenario_tag.txt`. You can do that by running: `PY_COLORS=0 molecule test > .molecule-results/2021-08-07-docker-snap.txt` (make sure to put PY_COLORS=0 at the beginning of the command so the colors are stripped).

2. Then, simply run `ansibler --generate-compatibility-chart` and a new `ansibler.json` will be generated, which will have your brand new compatibility chart under `compatibility_matrix`. It will look something like this:

```
"compatibility_matrix": [
    ["OS Family", "OS Version", "Status", "Idempotent", "Tested On"],
    ["Fedora", "33", "❌", "❌", "April 4th, 2006"],
    ["Ubuntu", "focal", "✅", "❌", "February 5th, 2009"],
    ["Windows", "10", "✅"", "✅"", "January 6th 2020"]
  ],
```

_TIP:_ Don't like the `.molecule-results` dir? No problem. You can tell Ansibler to use another directory by passing `--molecule-results-dir` - example:

`ansibler --generate-compatibility-chart --molecule-results-dir molecule/.results`

### Populating Platforms

You can also update your role's `meta/main.yml` so that `galaxy_info.platforms` matches the new `compatibility_matrix` chart. Simply run the following:

```
ansibler --populate-platforms
```

### Role Dependency Charts

Finally, you can also add dependency data to your role's `ansibler.json` file. Simply run:

```
ansibler --role-dependencies
```

Ansibler reads your dependencies from `requirements.yml` and then builds an additional depencency chart, which will be added under `role_dependencies` and will look something like the following:

```
{
  "role_dependencies": [
    [
      "Dependency",
      "Description",
      "Supported OSes",
      "Status"
    ],
    [
      "<b><a href=\"https://galaxy.ansible.com/professormanhattan/snapd\" title=\"professormanhattan.snapd on Ansible Galaxy\" target=\"_blank\">professormanhattan.snapd</a></b>",
      "Ensures Snap is installed and properly configured on Linux",
      "<a title=\"Windows 11 build status on GitHub\" href=\"https://gitlab.com/ProfessorManhattan/ansible-snapd/actions/Windows.yml\" target=\"_blank\"><img alt=\"Windows 11 build status\" src=\"https://img.shields.io/github/workflow/status/ProfessorManhattan/ansible-snapd/Windows/master?color=cyan&label=Windows%20build&logo=windows&style=flat\"></a><a title=\"macOS build status on GitHub\" href=\"https://gitlab.com/ProfessorManhattan/ansible-snapd/actions/macOS.yml\" target=\"_blank\"><img alt=\"macOS build status\" src=\"https://img.shields.io/github/workflow/status/ProfessorManhattan/ansible-androidstudio/macOS/master?label=macOS%20build&logo=apple&style=flat\"></a>"
    ],
    [
      "<b><a href=\"https://galaxy.ansible.com/professormanhattan/homebrew\" title=\"professormanhattan.homebrew on Ansible Galaxy\" target=\"_blank\">professormanhattan.homebrew</a></b>",
      "Installs Homebrew on nearly any OS",
      "For simplicity, this cell's data has not been added.",
      "<a title=\"Windows 11 build status on GitHub\" href=\"https://gitlab.com/ProfessorManhattan/ansible-homebrew/actions/Windows.yml\" target=\"_blank\"><img alt=\"Windows 11 build status\" src=\"https://img.shields.io/github/workflow/status/ProfessorManhattan/ansible-homebrew/Windows/master?color=cyan&label=Windows%20build&logo=windows&style=flat\"></a><a title=\"macOS build status on GitHub\" href=\"https://gitlab.com/ProfessorManhattan/ansible-homebrew/actions/macOS.yml\" target=\"_blank\"><img alt=\"macOS build status\" src=\"https://img.shields.io/github/workflow/status/ProfessorManhattan/ansible-androidstudio/macOS/master?label=macOS%20build&logo=apple&style=flat\"></a>"
    ]
  ]
}
```

_NOTE:_ the Status column gets generated by reading the `role_dependencies_status_format` field in `./variables.json` and then replacing all ocurrences of `role_name` with each dependency name.

You can also use a template file and populate it using an additional variables file - the two arguments for that:

- `--repository-status-template`: you can pass a filepath or a string.
- `--variables`: JSON file that defines the variables. Any ocurrences of `variable` in the template will be replaced with the corresponding variable in this JSON file.

_TIP:_ You can also run `ansibler --role-dependencies` in your playbooks. Ansibler will attempt to read your roles path (using `ansible-dump`) and generate role dependencies for ALL your roles!

<a href="#additional-info" style="width:100%"><img style="width:100%" src="https://gitlab.com/megabyte-labs/assets/-/raw/master/png/aqua-divider.png" /></a>

## Additional Info

### Caching

Ansibler generates a cache file under `~/.local/megabytelabs/ansibler` - you can clear it with:

```
ansibler --clear-cache
```

### Overriding ansibler.json and meta/main.yml

By default, Ansibler writes to (and reads from) `ansibler.json`. If you want to override this, add `--json-file` when you use Ansibler. For example:

```
ansibler --generate-compatibility-chart --json-file .example.json
ansibler --populate-platforms --json-file .example.json
ansibler --role-dependencies --json-file .example.json
```

### Help

```
ansibler --help
```

<a href="#installation" style="width:100%"><img style="width:100%" src="https://gitlab.com/megabyte-labs/assets/-/raw/master/png/aqua-divider.png" /></a>

## Installation

To accomodate everyone, this CLI can be installed using a variety of methods.

### PyPi

If you already have Python 3 and pip3 installed, you can install the CLI by running:

```shell
pip3 install {{(if customPyPiPackageName customPyPiPackageName (append repository.prefix.github slug))}}
```

### Install Doctor

On **macOS or Linux**, you can run:

```shell
bash -sS https://install.doctor/py/{{(if customPyPiPackageName customPyPiPackageName (append repository.prefix.github slug))}}
```

And on **Windows**, you can run:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://install.doctor/py/{{(if customPyPiPackageName customPyPiPackageName (append repository.prefix.github slug))}}?os=win'))
```

### Homebrew

If you have [Homebrew](https://brew.sh/) installed, you can install the package by running:

```shell
brew install installdoc/py/{{(if customPyPiPackageName customPyPiPackageName (append repository.prefix.github slug))}}
```

Or if you prefer to keep Python off your system, and install a binary, you can run:

```shell
brew install installdoc/py/{{(if customPyPiPackageName customPyPiPackageName (append repository.prefix.github slug))}}-binary
```

### Chocolatey

If you are on Windows, you can install a binary version (without the Python dependency), using [Chocolatey](https://chocolatey.org/):

```powershell
choco install {{(if customPyPiPackageName customPyPiPackageName (append repository.prefix.github slug))}}
```

### Binary Releases

There are also binaries (in various formats) available for download on both [GitHub](https://github.com/ProfessorManhattan/ansibler/releases) and [GitLab](https://gitlab.com/megabyte-labs/python/cli/ansibler/-/releases).

<a href="#requirements" style="width:100%"><img style="width:100%" src="https://gitlab.com/megabyte-labs/assets/-/raw/master/png/aqua-divider.png" /></a>

## Requirements

To run this project, all you need is [Python 3](https://www.python.org/) and [pip3](https://pip.pypa.io/en/stable/). See the [Installation section](#installation) for instructions that include alternate installation methods that do not require Python to be installed.

If you are interested in contributing or would like to make some modifications, please see the [CONTRIBUTING](/docs/CONTRIBUTING.md) guide. There are a handful of build tools we incorporate into the development process. All of them are installed automatically via our Taskfile system. You can get started customizing this project by running:

```shell
bash .config/scripts/start.sh
task start
task --list
```

<a href="#contributing" style="width:100%"><img style="width:100%" src="https://gitlab.com/megabyte-labs/assets/-/raw/master/png/aqua-divider.png" /></a>

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/ProfessorManhattan/ansibler/issues). If you would like to contribute, please take a look at the [contributing guide](https://github.com/ProfessorManhattan/ansibler/blob/master/docs/CONTRIBUTING.md).

<details>
<summary><b>Sponsorship</b></summary>
<br/>
<blockquote>
<br/>
Dear Awesome Person,<br/><br/>
I create open source projects out of love. Although I have a job, shelter, and as much fast food as I can handle, it would still be pretty cool to be appreciated by the community for something I have spent a lot of time and money on. Please consider sponsoring me! Who knows? Maybe I will be able to quit my job and publish open source full time.
<br/><br/>Sincerely,<br/><br/>

**_Brian Zalewski_**<br/><br/>

</blockquote>

<a title="Support us on Open Collective" href="https://opencollective.com/megabytelabs" target="_blank">
  <img alt="Open Collective sponsors" src="https://img.shields.io/opencollective/sponsors/megabytelabs?logo=opencollective&label=OpenCollective&logoColor=white&style=for-the-badge" />
</a>
<a title="Support us on GitHub" href="https://github.com/ProfessorManhattan" target="_blank">
  <img alt="GitHub sponsors" src="https://img.shields.io/github/sponsors/ProfessorManhattan?label=GitHub%20sponsors&logo=github&style=for-the-badge" />
</a>
<a href="https://www.patreon.com/ProfessorManhattan" title="Support us on Patreon" target="_blank">
  <img alt="Patreon" src="https://img.shields.io/badge/Patreon-Support-052d49?logo=patreon&logoColor=white&style=for-the-badge" />
</a>

</details>

<a href="#license" style="width:100%"><img style="width:100%" src="https://gitlab.com/megabyte-labs/assets/-/raw/master/png/aqua-divider.png" /></a>

## License

Copyright © 2020-2021 [Megabyte LLC](https://megabyte.space). This project is [MIT](https://gitlab.com/megabyte-labs/python/cli/ansibler/-/blob/master/LICENSE) licensed.
