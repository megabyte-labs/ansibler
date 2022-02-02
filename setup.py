from setuptools import setup, find_packages

setup(
    name="ansibler",
    packages=find_packages(),
    version="0.2.4",
    license="MIT",
    description="Generate JSON data that describes the dependencies of an "
    "Ansible playbook/role. Also, automatically generate OS compatibil"
    "ity charts using Molecule.",
    author="Renny Montero",
    author_email="rennym19@gmail.com",
    url=f"https://gitlab.com/megabyte-labs/python/cli/ansibler",
    download_url=f"https://gitlab.com/megabyte-labs/python/{REPO}/archive/",
    keywords=["ANSIBLE", "DEPENDENCY", "ROLE", "MOLECULE", "CHARTS", "TEST"],
    install_requires=[
        "ruamel.yaml",
        "requests",
    ],
    include_package_data=True,
    entry_points={"console_scripts": [f"{NAME} = ansibler.run:main"]},
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
