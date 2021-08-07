# Ansibler

Generate JSON data that describes the dependencies of an Ansible playbook/role. Also, automatically generate OS compatibility charts using Molecule.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)

## Requirements
- [Python 3.6+](https://www.python.org/downloads/)

## Installation

You can install Ansibler using pip:

```sh
pip3 install ansibler
```

## Usage

With Ansibler, you can extract both role dependencies and OS compatibility data with the help of [Molecule Tests](https://molecule.readthedocs.io/en/latest/).

<br/>

---
### Generating Compatibility Charts
Say you have run `molecule test` and want to generate updated compatibility charts for your role using the test's output. With Ansibler, it's possible to do just that!

1. Start by dumping the results of your test to `./.molecule-results/YEAR-MONTH-DAY-scenario_tag.txt`. You can do that by running: `PY_COLORS=0 molecule test > .molecule-results/2021-08-07-docker-snap.txt` (make sure to put PY_COLORS=0 at the beginning of the command so the colors are stripped).

2. Then, simply run `ansibler --generate-compatibility-chart` and a new `package.ansibler.json` will be generated, which will just be a copy of your current package.json, but with the addition of your brand new compatibility chart under `blueprint.compatibility`. It will look something like this:

```
"compatibility": [
    ["OS Family", "OS Version", "Status", "Idempotent", "Tested On"],
    ["Fedora", "33", "❌", "❌", "April 4th, 2006"],
    ["Ubuntu", "focal", "✅", "❌", "February 5th, 2009"],
    ["Windows", "10", "✅"", "✅"", "January 6th 2020"]
  ],
```

*TIP:* Don't like the `.molecule-results` dir? No problem. You can tell Ansibler to use another directory by passing `--molecule-results-dir` - example:

```ansibler --generate-compatibility-chart --molecule-results-dir molecule/.results```

<br/>

---
### Populating Platforms
You can also update your role's `meta/main.yml` so that `galaxy_info.platforms` matches the new `blueprint.compatibility` chart. Simply run the following:
```
ansibler --populate-platforms
```

*NOTE:* by default, Ansibler does not override `meta/main.yml`. Instead, it will create and write to a new file: `meta/main.ansibler.yml`.

<br/>

---
### Role Dependency Charts
Finally, you can also add dependency data to your role's `package.ansibler.json` file. Simply run:

```
ansibler --role-dependencies
```

Ansibler reads your dependencies from `requirements.yml` and then builds an additional depencency chart, which will be added under `blueprint.role_dependencies` and will look something like the following:

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
      "<img src=\"https://gitlab.com/megabyte-labs/assets/-/raw/master/icon/centos.png\" /><img src=\"https://gitlab.com/megabyte-labs/assets/-/raw/master/icon/fedora.png\" /><img src=\"https://gitlab.com/megabyte-labs/assets/-/blob/master/icon/ubuntu.png\" /><img src=\"https://gitlab.com/megabyte-labs/assets/-/blob/master/icon/debian.png\" />",
      "<a href=\"https://gitlab.com/megabyte-labs/ansible-roles/snapd\" title=\"professormanhattan.snapd's repository\" target=\"_blank\"><img src=\"https://gitlab.com/megabyte-labs/ansible-roles/snapd/badges/master/pipeline.svg\" /></a>"
    ],
    [
      "<b><a href=\"https://galaxy.ansible.com/professormanhattan/homebrew\" title=\"professormanhattan.homebrew on Ansible Galaxy\" target=\"_blank\">professormanhattan.homebrew</a></b>",
      "Installs Homebrew on nearly any OS",
      "For simplicity, this cell's data has not been added.",
      "<a href=\"https://gitlab.com/megabyte-labs/ansible-roles/homebrew\" title=\"professormanhattan.homebrew's repository\" target=\"_blank\"><img src=\"https://gitlab.com/megabyte-labs/ansible-roles/homebrew/badges/master/pipeline.svg\" /></a>"
    ]
  ]
}
```

*TIP:* You can also run `ansibler --role-dependencies` in your playbooks. Ansibler will attempt to read your roles path (using `ansible-dump`) and generate role dependencies for ALL your roles!

<br>

---
## Additional Info
### Caching
Ansibler generates a cache file under `~/.local/megabytelabs/ansibler` - you can clear it with:
```
ansibler --clear-cache
```

### Overwriting package.json and meta/main.yml
By default, Ansibler does not overwrite your files. If you want it to overwrite either `package.json` or `meta/main.yml`, add `--inline-replace` when you use Ansibler. For example:
```
ansibler --populate-platforms --inline-replace
```

### Help
```
ansibler --help
```
