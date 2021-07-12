from os import name
import os
from pathlib import Path
from ansgen.task import Task
from ansgen.playbook import Playbook


def generate_windows_playbook():
    pb = Playbook(name="Windows Playbook for all Hosts", hosts="all")

    ensure_path = Task(
        name="Ensure Path variables exist",
        properties={
            "ansible.windows.win_path": {
                "elements": os.environ["PATH"].split(';'),
                "state": "present"
            }
        },
    )

    pb.tasks.append(ensure_path)

    Path("generated_files/windows").mkdir(parents=True, exist_ok=True)
    with open("generated_files/windows/playbook.yaml", "w") as file:
        pb.write(file)
