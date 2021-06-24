import glob
import gzip
import re
import os
from pathlib import Path


class Playbook:
    name = "Deploy locally"
    hosts = "localhost"
    become = True
    tasks = []

    def write(self, file):
        file.write(f"- name: {self.name}\n")
        file.write(" "*2 + f"hosts: {self.hosts}\n")
        if self.become:
            file.write(" "*2 + "become: yes\n")
        file.write(" "*2 + "tasks:\n")
        for task in self.tasks:
            task.write(file, 4)


class Task:
    name = None
    properties = None

    def write(self, file, base_indent):
        if self.properties is not None:
            file.write(" "*base_indent + f"- name: {self.name}\n")
            for key, value in self.properties.items():
                file.write(" "*(base_indent+2) + f"{key}:")
                self.write_property(value, file, base_indent+4)

    def write_property(self, property, file, indent):
        if isinstance(property, list):
            file.write("\n")
            for item in property:
                file.write(" "*indent + f"- {item}\n")
        elif isinstance(property, dict):
            file.write("\n")
            for key, value in property.items():
                file.write(" "*indent + f"{key}:")
                self.write_property(value, file, indent+2)
        else:
            file.write(f" {property}\n")

    def __init__(self, name, properties: dict) -> None:
        self.name = name
        self.properties = properties


def installed_apt_packages():
    packages = []
    files = glob.glob("/var/log/apt/history.log*")
    regex = re.compile("^Commandline: (apt-get|apt|/usr/bin/apt.*) install (.*)")
    for file in files:
        if file.endswith("gz"):
            with gzip.open(file) as f:
                for line in f:
                    match = regex.search(line.decode("utf-8"))
                    if match is not None:
                        packages.append(match.group(2))
        else:
            with open(file) as f:
                for line in f:
                    match = regex.search(line)
                    if match is not None:
                        packages.append(match.group(2))
    return packages
    # zgrep -hPo '^Commandline: (apt-get|apt) install (?!.*--reinstall)\K.*' /var/log/apt/history.log{.*.gz,}

def removed_apt_packages():
    packages = []
    files = glob.glob("/var/log/apt/history.log*")
    regex = re.compile("^Commandline: (apt-get|apt|/usr/bin/apt.*) remove (.*)")
    for file in files:
        if file.endswith("gz"):
            with gzip.open(file) as f:
                for line in f:
                    match = regex.search(line.decode("utf-8"))
                    if match is not None:
                        packages.append(match.group(2))
        else:
            with open(file) as f:
                for line in f:
                    match = regex.search(line)
                    if match is not None:
                        packages.append(match.group(2))
    return packages
    # zgrep -hPo '^Commandline: (apt-get|apt) install (?!.*--reinstall)\K.*' /var/log/apt/history.log{.*.gz,}


def installed_snap_packages():
    snap_packages = []
    stream = os.popen('snap list | awk \'{print $1}\'')
    output = list(stream.readlines())
    output = output[1:]
    snap_packages = list(map(lambda x: x.strip('\n'), output))
    return snap_packages

def main():
    pb = Playbook()
    packages_to_install = installed_apt_packages()
    packages_to_remove = removed_apt_packages()
    intersection = set.intersection(set(packages_to_install), set(packages_to_remove))
    packages_to_install = list(set(packages_to_install) - intersection)
    packages_to_remove = list(set(packages_to_remove) - intersection)
    snap_packages_to_install = installed_snap_packages()
    install_packages = Task(
        name="Install apt packages",
        properties={
            "apt": {
                "state": "present",
                "name": packages_to_install,
            },
        },
    )
    remove_packages = Task(
        name="Remove apt packages",
        properties={
            "apt": {
                "state": "absent",
                "name": packages_to_remove,
            },
        },
    )
    install_snap_packages = Task(
        name="Install snap packages",
        properties={
            "community.general.snap": {
                "name": snap_packages_to_install,
            },
        },
    )
    pb.tasks.append(install_packages)
    pb.tasks.append(remove_packages)
    pb.tasks.append(install_snap_packages)
    Path("generated_files").mkdir(parents=True, exist_ok=True)
    with open("generated_files/playbook.yaml", "w") as file:
        pb.write(file)

if __name__ == "__main__":
    main()
