import os
import re
import pwd
import glob
import gzip
from pathlib import Path
from shutil import copyfile, which
from ansgen.task import Task
from ansgen.playbook import Playbook


def generate_unix_playbook(plugins):
    user = get_username()

    pb = Playbook(become=True)
    packages_to_install = installed_apt_packages()
    packages_to_remove = removed_apt_packages()
    packages_to_install = list(set(packages_to_install) - set(packages_to_remove))

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

    pb.tasks.append(install_packages)
    pb.tasks.append(remove_packages)

    if is_tool('snap'):
        snap_packages_to_install = installed_snap_packages()
        install_snap_packages = Task(
            name="Install snap packages",
            properties={
                "community.general.snap": {
                    "name": snap_packages_to_install,
                },
            },
        )
        pb.tasks.append(install_snap_packages)

    copy_env_files()

    copy_user_env = Task(
        f"Copy environment files for user {user}",
        properties={
            "become_user": user,
            "template": {
                "src": "\"{{ item.src }}\"",
                "dest": "\"{{ item.dest }}\"",
                "mode": "0644",
            },
            "loop": [
                f'{{ src: "./env_files/{user}/.bashrc", dest: "~/.bashrc" }}',
                f'{{ src: "./env_files/{user}/.profile", dest: "~/.profile" }}'
            ]
        },
    )

    copy_sys_env = Task(
        "Copy system environment",
        properties={
            "ansible.builtin.copy": {
                "src": "\"./env_files/environment\"",
                "dest": "\"/etc/environment\"",
                "mode": "0644",
            }
        }
    )

    pb.tasks.append(copy_user_env)
    pb.tasks.append(copy_sys_env)

    for plugin in plugins:
        if plugin.canRun():
            plugin.run(pb)

    Path("generated_files/unix").mkdir(parents=True, exist_ok=True)
    with open("generated_files/unix/playbook.yaml", "w") as file:
        pb.write(file)


def get_username():
    return pwd.getpwuid( os.getuid() )[ 0 ]

def is_tool(name):
    """Check whether `name` is on PATH and marked as executable."""

    return which(name) is not None


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


def copy_env_files():
    user = get_username()
    # ~/.bashrc
    bashrc_src = str(os.path.expanduser('~/.bashrc'))
    bashrc_dest = f"./generated_files/env_files/{user}/.bashrc"
    os.makedirs(os.path.dirname(bashrc_dest), exist_ok=True)
    copyfile(bashrc_src, bashrc_dest)

    # ~/.bash_aliases
    bash_aliases_src = str(os.path.expanduser('~/.bash_aliases'))
    bash_aliases_dest = f"./generated_files/env_files/{user}/.bash_aliases"
    if Path(bash_aliases_src).is_file():
        os.makedirs(os.path.dirname(bash_aliases_dest), exist_ok=True)
        copyfile(bash_aliases_src, bash_aliases_dest)

    # ~/.profile
    profile_src = str(os.path.expanduser('~/.profile'))
    profile_dest = f"./generated_files/env_files/{user}/.profile"
    os.makedirs(os.path.dirname(profile_dest), exist_ok=True)
    copyfile(profile_src, profile_dest)

    # ~/.pam_environment
    pam_src = str(os.path.expanduser('~/.pam_environment'))
    pam_dest = f"./generated_files/env_files/{user}/.pam_environment"
    if Path(pam_src).is_file():
        os.makedirs(os.path.dirname(pam_dest), exist_ok=True)
        copyfile(pam_src, pam_dest)

    # /etc/environment
    env_src = "/etc/environment"
    env_dest = "./generated_files/env_files/environment"
    os.makedirs(os.path.dirname(env_dest), exist_ok=True)
    copyfile(env_src, env_dest)

    # /etc/profile.d/profile_ans.sh
    script_src = "/etc/profile.d/profile_ans.sh"
    script_dest = "./generated_files/env_files/profile_ans.sh"
    if Path(pam_src).is_file():
        os.makedirs(os.path.dirname(script_dest), exist_ok=True)
        copyfile(script_src, script_dest)


def installed_snap_packages():
    snap_packages = []
    stream = os.popen('snap list | awk \'{print $1}\'')
    output = list(stream.readlines())
    output = output[1:]
    snap_packages = list(map(lambda x: x.strip('\n'), output))
    return snap_packages
