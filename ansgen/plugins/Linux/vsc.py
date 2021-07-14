from .base import *
from pathlib import Path
from shutil import copyfile, which
import os
import pwd

def get_username():
    return pwd.getpwuid( os.getuid() )[ 0 ]

class Plugin(BasePlugin):

    def canRun(self):

        return which('code') is not None

    def save_extensions(self, pb):

        vsc_extensions_stream = os.popen('code --list-extensions | xargs -L 1 echo code --install-extension')
        Path("generated_files/vsc").mkdir(parents=True, exist_ok=True)
        with open("generated_files/vsc/extensions", "w") as file:
            file.writelines(vsc_extensions_stream)

        install_extensions = Task(
            name="Install vsc extensions",
            properties={
                "command": "\"{{ item }}\"",
                "loop" : "\"{{ lookup('file', './vsc/extensions').splitlines() }}\""
            },
        )

        pb.tasks.append(install_extensions)

    def ensure_code_installation(self, pb):

        install_vsc = Task(
            name="Install vsc via apt",
            properties={
                "apt": {
                    "state": "present",
                    "name": ['code'],
                },
            },
        )
        pb.tasks.append(install_vsc)

    def save_settings(self, pb):

        user = get_username()
        settings_src = str(os.path.expanduser('~/.config/Code/User/settings.json'))
        settings_dst = f"./generated_files/vsc/{user}/settings.json"
        os.makedirs(os.path.dirname(settings_dst), exist_ok=True)
        copyfile(settings_src, settings_dst)

        copy_user_settings = Task(
            f"Copy vsc Settings for user {user}",
            properties={
                "become_user": user,
                "template": {
                    "src": "\"{{ item.src }}\"",
                    "dest": "\"{{ item.dest }}\"",
                    "mode": "0644",
                },
                "loop": [
                    f'{{ src: "./generated_files/vsc/{user}/settings.json", dest: "~/.config/Code/User/settings.json" }}',
                ]
            },
        )

        pb.tasks.append(copy_user_settings)

    def run(self, playBook):

        self.ensure_code_installation(playBook)
        self.save_extensions(playBook)
        self.save_settings(playBook)
