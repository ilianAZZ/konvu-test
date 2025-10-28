import os
from typing import Dict


class Dependency(Dict):
    name: str
    version: str | None
    ecosystem: str
    environment: str | None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = kwargs.get('name')
        self.version = kwargs.get('version')
        self.ecosystem = kwargs.get('ecosystem')
        self.environment = kwargs.get('environment')

    def __str__(self):
        env = f" ({self.environment})" if self.environment else ""
        ver = f" v{self.version}" if self.version else ""
        return f"{self.name}{ver} [{self.ecosystem}{env}]"

###
# Helpers to parse different dependency files
###


def read_file_lines(file_path):
    with open(file_path, 'r') as f:
        return f.readlines()


def exists(codebase_path: str, file_path: str):
    return os.path.isfile(os.path.join(codebase_path, file_path))

###
# Parsers for different dependency files
###


def parse_requirements(file_path: str) -> list[Dependency]:
    """
    Parse a requirements.txt file and return a list of dependencies.
    Args:
        file_path (str): Path to the requirements.txt file.
    Returns:
        list[Dependency]: List of dependencies with name and version.
    """
    lines = read_file_lines(file_path)
    deps = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            if '==' in line:
                name, version = line.split('==')
                deps.append(Dependency(name=name.strip(),
                            version=version.strip(), ecosystem='PyPI'))
            else:
                deps.append(Dependency(name=line.strip(),
                            version=None, ecosystem='PyPI'))
    return deps


def parse_package_json(file_path: str) -> list[Dependency]:
    """
    Parse a package.json file and return a list of dependencies.
    Args:
        file_path (str): Path to the package.json file.
    Returns:
        list[Dependency]: List of dependencies with name and version.
    """
    import json
    with open(file_path, 'r') as f:
        data = json.load(f)

    deps = []
    for dep_type in ['dependencies', 'devDependencies']:

        env = 'production' if dep_type == 'dependencies' else 'development'

        if dep_type in data:
            for name, version in data[dep_type].items():
                deps.append(Dependency(name=name, version=version,
                            ecosystem='npm', environment=env))
    return deps


def scan_dependencies(codebase_path) -> list[Dependency]:
    deps = []

    # Python
    if exists(codebase_path, 'requirements.txt'):
        file_path = os.path.join(codebase_path, 'requirements.txt')
        deps += parse_requirements(file_path)

    # Node.js
    # TODO parse package-lock.json or yarn.lock for more accurate versions
    if exists(codebase_path, 'package.json'):
        file_path = os.path.join(codebase_path, 'package.json')
        deps += parse_package_json(file_path)

    return deps
