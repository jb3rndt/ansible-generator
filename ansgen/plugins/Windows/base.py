from abc import ABCMeta, abstractmethod
import sys
import os
baseDir = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir, os.pardir, os.pardir))
sys.path.append(baseDir)
from task import Task

class BasePlugin():
    __metaclass__ = ABCMeta

    @abstractmethod
    def canRun(self):
        """Perform checks, whether your plugin can run or not here.
           Return `True` if your plugin can Run."""
        pass

    @abstractmethod
    def run(self, playbook):
        """Method to append your plugins tasks to the playbook"""
        pass