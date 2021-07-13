from .base import *


class Plugin(BasePlugin):

    def canRun(self):
        return True

    def run(self, playBook):
        test = Task(name="Dummy Plugin Test",
                    properties={
                    "apt": {
                        "state": "present",
                        "name": "test",
                        }
                    })
        playBook.tasks.append(test)
