class Playbook:
    def __init__(self, name=None, hosts=None, become=None, tasks=None):
        self.name = name or "Deploy locally"
        self.hosts = hosts or "localhost"
        self.become = become or False
        self.tasks = tasks or []

    def write(self, file):
        file.write(f"- name: {self.name}\n")
        file.write(" "*2 + f"hosts: {self.hosts}\n")
        if self.become:
            file.write(" "*2 + "become: yes\n")
        file.write(" "*2 + "tasks:\n")
        for task in self.tasks:
            task.write(file, 4)
