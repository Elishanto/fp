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
            allowed = set(['name', 'email', 'wt', 'ht', 'password'])
            task = json.loads(self.get_argument("aim").strip())
            if len(set(task.keys()) - allowed) > 0: 
                print('DEB', set(task.keys()) - allowed)
                self.write(Api.generate_request_return(-90))
                self.finish()
                return

            task['opened_ex'] = (10,)
            task['valid'] = 1
            self.insert_data('users', task)
            self.write(Api.generate_request_return(1))
