from setuptools import setup, find_packages
from ansibler import __version__, name

NAME = name
REPO = name

VERSION = __version__
ARCHIVE = f"v_{'_'.join(VERSION.split('.'))}.tar.gz"

setup(
    name=NAME,
    packages=find_packages(),
    version=VERSION,
    license="MIT",
    description="Generate JSON data that describes the dependencies of an " \
        "Ansible playbook/role. Also, automatically generate OS compatibil" \
        "ity charts using Molecule.",
    author="Renny Montero",
    author_email="rennym19@gmail.com",
    url=f"https://gitlab.com/megabyte-labs/python/{REPO}/",
    download_url=f"https://gitlab.com/megabyte-labs/python/{REPO}/archive/" \
        f"{ARCHIVE}",
    keywords=["ANSIBLE", "DEPENDENCY", "ROLE", "MOLECULE", "CHARTS", "TEST"],
    install_requires=[
        "ruamel.yaml"
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [f"{NAME} = ansibler.run:main"]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
