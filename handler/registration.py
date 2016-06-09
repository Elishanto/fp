import json
import os
from handler import BaseHandler
from api.baseapi import Api

description = os.environ['description']


class RegistrationHandler(BaseHandler):
    def get(self, url):
        self.render('../static/register_activity.html')

    def post(self, url=None):
        lake = self.get_argument("lake").lower().strip()  # global/exID
        if lake == 'global':
            allowed = ('name', 'email', 'wt', 'ht')
            task = json.loads(self.get_argument("aim").strip())
            for i in task.keys():
                if i not in allowed:
                    self.write(Api.generate_request_return(-90))
                    self.finish()
            task['valid'] = 1
            self.insert_data('users', task)
            self.write(Api.generate_request_return(1))
