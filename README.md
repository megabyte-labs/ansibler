# Ansibler

Ansibler should support the following parameters:

* **--generate-compatibility-chart** - (e.g. `ansibler --generate-compatibility-chart`) This command should generate a piece of data stored in `package.json` under `blueprint.compatibility` that details the supported OSes.
* **--populate-platforms** - (e.g. `ansibler --populate-platforms`) This command should populate the platforms variable in the `galaxy_info` of `meta/main.yml`. If `meta/main.yml` is missing then output an error message that says `meta/main.yml` is missing.
* **--role-dependencies** - (e.g. `ansibler --role-dependencies`) This command should generate a chart with useful information about the dependencies of the role/playbook.

## Generating the Compatibility Chart

The compatibility chart should be generated using information from two different sources:

* The test results in the `.molecule-results` folder
* `tasks/main.yml`

The test results in the `.molecule-results` folder should all be Molecule test results that come from running the command `molecule test` command in each role. You can generate some sample data by cloning the Playbooks repository, navigating to a role (e.g. `/roles/tools/nmap`), installing the requirements (e.g. pip3 install -r requirements.txt), and then running `PY_COLORS=0 molecule test > .molecule-results/2021-05-01-tagname.txt`. You will need Docker/VirtualBox installed depending on the scenario you choose to run. `molecule test` uses the scenario in `molecule/default`. If you want to run it with Docker instead of VirtualBox, you can run `molecule test -s docker-snap` or `molecule test -s docker`. Each scenario correponds to a folder in the `molecule/` folder.

After you generate a couple log files by piping the ouput of `molecule test` to a txt file, you can then inspect the results to get a feel for which tests successfully installed the software and which tests passed the Idempotency test. Please reach out to me if you have any questions about this. When running the tests and saving the data, ensure to put PY_COLORS=0 at the beginning of the command so the colors are stripped.

During your testing, populate the `.molecule-results/` folder with a couple tests. Name each test `YEAR-MONTH-DAY-scenario_tag.txt`.

After you have some sample data ready, `ansibler --generate-compatibility-chart` should scan each of the results in the `.molecule-results/` folder and grab the result for the most recent test of each operating system. It is necessary to do it like this because no test will cover all OSes at the same time. One test might test Windows, another all the Linux systems, and another MacOSX. Ensure to first grab whether or not something successfully installed and then, if the test includes a Idempotency test, then grab that information too. With all the information gathered, you should be able to add a variable to `package.json` under `blueprint.compatibility` that looks something like this:

```
"compatibility": [
    ["OS Family", "OS Version", "Status", "Idempotent", "Tested On"],
    ["Fedora", "33", "❌", "❌", "April 4th, 2006"],
    ["Ubuntu", "focal", "✅", "❌", "February 5th, 2009"],
    ["Windows", "10", "✅"", "✅"", "January 6th 2020"]
  ],
```

### `tasks/main.yml`

For now, skip this part of the project. I am just adding details here in case you're interested in prepping for the future. All of the Ansible roles in the Playbooks repository are made so that they successfully can run against any system. However, some of them do not execute logic on certain systems. We need to filter out the compatibility chart so that it only contains data about the operating systems that the role is meant to run against. Taking the above `compatibility` JSON as an example. If we had a `tasks/main.yml` file that looked like this:

```
- name: Execute logic
  include: task.yml
  when: ansible_os_family == 'Windows'
```

Then the compatibility chart data above should be stripped of the entries that contain the operating systems that do not run any logic. There are ways we can make this easier to implement so hold off on this section for now.

## Populating Platforms in `meta/main.yml`

When the user runs `ansibler --populate-platforms`, Ansibler should use information from the `blueprint.compatibility` data in `package.json` to determine the platforms that the role supports. The script should look at the `blueprint.compatibility` variable in `package.json`. The variable will look something like this:

```
"compatibility": [
    ["OS Family", "OS Version", "Status", "Idempotent", "Tested On"],
    ["Fedora", "33", "❌", "❌", "April 4th, 2006"],
    ["Ubuntu", "focal", "✅", "❌", "February 5th, 2009"],
    ["Windows", "10", "✅"", "✅"", "January 6th 2020"]
  ],
```

And will ultimately be included in the README.md in the following format:

| OS Family | OS Version | Status | Idempotent | Tested On          |
|-----------|------------|--------|------------|--------------------|
| Fedora    | 33         | ❌     | ❌          | April 4th, 2006    |
| Ubuntu    | focal      | ✅     | ❌          | February 5th, 2009 |
| Windows   | 10         | ✅     | ✅          | January 6th, 2020  |

With the chart above, the platforms in galaxy_info (located in `meta/main.yml`) should be (NOTE: Fedora is missing):

```
  platforms:
    - name: Ubuntu
      versions:
        - focal
    - name: Windows
      versions:
        - all
```

Windows is special because even though it is version 10, we mark it as all in the platforms variable.

## Generating Role Dependency Charts

Regardless of whether the project is a role or playbook, the following logic is used at first:

1. Acquires an array of `roles_path` paths by running `ansible-config dump` and then acquiring the array of paths. The value in the paths variable in the dump should look something like this: `DEFAULT_ROLES_PATH(/Users/MyUser/Playbooks/ansible.cfg) = ['/Users/MyUser/Playbooks/roles/applications', '/Users/MyUser/Playbooks/roles/crypto', '/Users/MyUser/Playbooks/roles/helpers', '/Users/MyUser/Playbooks/roles/languages', '/Users/MyUser/Playbooks/roles/misc', '/Users/MyUser/Playbooks/roles/services', '/Users/MyUser/Playbooks/roles/system', '/Users/MyUser/Playbooks/roles/tools', '/Users/MyUser/Playbooks/roles/virtualization', '/Users/MyUser/.ansible/roles', '/usr/share/ansible/roles', '/etc/ansible/roles']`
2. Creates a cached map of the important meta information in each role found in one of the paths. For each role found in one of the paths, `ansibler` will look for a `meta/main.yml` file and extract the `role_name`, `namespace`, and `description`. The cache should then store the folder name = description. The idea of having a cache is to make the process FAST. It is common for the project to be able to live reload every 10s-20s. The cached map should be stored in `~/.local/megabytelabs/ansibler`. A typical `meta/main.yml` will look something like this:

```
---
galaxy_info:
  role_name: snapd
  author: professormanhattan
  description: Ensures Snap is installed and properly configured on Linux
  company: Megabyte Labs
  license: license (MIT)
  repository: https://gitlab.com/megabyte-labs/ansible-roles/snapd
  repository_status: https://gitlab.com/megabyte-labs/ansible-roles/snapd/badges/master/pipeline.svg

  min_ansible_version: 2.10

  platforms:
    - name: EL
      versions:
        - 7
        - 8
    - name: Fedora
      versions:
        - 33
    - name: Ubuntu
      versions:
        - focal
    - name: Debian
      versions:
        - all

  galaxy_tags:
    - snap
    - snapd
    - package
    - installation
    - software
    - linux

dependencies: []
```

3. Next, since the descriptions are available, Ansibler generates a piece of JSON that is compatible with `@appnest/readme` which can be used to display a chart detailing the dependencies of an Ansible role/playbook. It does this by looking at the `requirements.yml`. For each role under the roles section in `requirements.yml`, the cached map of values should be used to determine the `description`. A typical `requirements.yml` will look something like this:

```
---
roles:
  - name: professormanhattan.snapd
  - name: professormanhattan.homebrew
collections:
  - name: chocolatey.chocolatey
    source: https://galaxy.ansible.com
  - name: community.general
    source: https://galaxy.ansible.com
```

4. For the `requirements.yml` file above, Ansibler should generate a JSON chart that looks something like this:

```
{
  "role_dependencies": [
    [
      "Role Dependency",
      "Description",
      "Supported OSes",
      "Status"
    ],
    [
      "<a href=\"https://galaxy.ansible.com/professormanhattan/snapd\" title=\"professormanhattan.snapd on Ansible Galaxy\" target=\"_blank\">professormanhattan.snapd</a>",
      "Ensures Snap is installed and properly configured on Linux",
      "<img src=\"https://gitlab.com/megabyte-labs/assets/-/raw/master/icon/centos.png\" /><img src=\"https://gitlab.com/megabyte-labs/assets/-/raw/master/icon/fedora.png\" /><img src=\"https://gitlab.com/megabyte-labs/assets/-/blob/master/icon/ubuntu.png\" /><img src=\"https://gitlab.com/megabyte-labs/assets/-/blob/master/icon/debian.png\" />",
      "<a href=\"https://gitlab.com/megabyte-labs/ansible-roles/snapd\" title=\"professormanhattan.snapd's repository\" target=\"_blank\"><img src=\"https://gitlab.com/megabyte-labs/ansible-roles/snapd/badges/master/pipeline.svg\" /></a>"
    ],
    [
      "<a href=\"https://galaxy.ansible.com/professormanhattan/homebrew\" title=\"professormanhattan.homebrew on Ansible Galaxy\" target=\"_blank\">professormanhattan.homebrew</a>",
      "Installs Homebrew on nearly any OS",
      "For simplicity, this cell's data has not been added.",
      "<a href=\"https://gitlab.com/megabyte-labs/ansible-roles/homebrew\" title=\"professormanhattan.homebrew's repository\" target=\"_blank\"><img src=\"https://gitlab.com/megabyte-labs/ansible-roles/homebrew/badges/master/pipeline.svg\" /></a>"
    ]
  ]
}
```

5. In the JSON above, you will see that the `Role Dependency` column uses a link in the form of `https://galaxy.ansible.com/{{ galaxy_info.namespace }}/{{ galaxy_info.role_name }}` with the text anchor as `{{ galaxy_info.namespace }}.{{ galaxy_info.role_name }}`. The description column is simply the text from `{{ galaxy_info.description }}`. The next column lists an array of icons that correlate to the operating systems that the role supports. These columns should be determined by looking at `{{ galaxy_info.platforms }}` (See the Icons section below for more details). Finally, the last `Status` column has a link in the form of `{{ galaxy_info.repository }}` and an image of `{{ galaxy_info.repository_status }}`. For the last column, if the `repository` field is unavailable then simply show the img. And if the `repository_status` is unavailable then replace the entire cell with 'Unavailable' text.

**The role_dependencies variable should be saved to `blueprint.role_dependencies` in package.json**

### Role Dependency Chart Icons

The third column in the `role_dependencies` chart displays icons that correlate to the platforms that are supported by the role. These icons should be determined by looking at the `{{ galaxy_info.platforms }}` variable. If there is an entry that says `Fedora` then the Fedora icon should show up. If there is a platform that says EL (which stands for Enterprise Linux) then the CentOS icon should show up. Here are the icons/platform names:

* **Archlinux** - https://gitlab.com/megabyte-labs/assets/-/raw/master/icon/archlinux.png
* **EL** - https://gitlab.com/megabyte-labs/assets/-/raw/master/icon/centos.png
* **Debian** - https://gitlab.com/megabyte-labs/assets/-/raw/master/icon/debian.png
* **Fedora** - https://gitlab.com/megabyte-labs/assets/-/raw/master/icon/fedora.png
* **FreeBSD** - https://gitlab.com/megabyte-labs/assets/-/raw/master/icon/freebsd.png
* **MacOSX** - https://gitlab.com/megabyte-labs/assets/-/raw/master/icon/macos.png
* **Ubuntu** - https://gitlab.com/megabyte-labs/assets/-/raw/master/icon/ubuntu.png
* **Windows** - https://gitlab.com/megabyte-labs/assets/-/raw/master/icon/windows.png

### Additional Notes

Although not shown in the example `role_dependencies` chart above, each icon in the `Supported OSes` column should link to `{{ galaxy_info.repository }}#supported-operating-systems`. All links should also include `target="_blank"`.
