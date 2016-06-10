import json
import os
from handler import BaseHandler
from api.baseapi import Api
description = os.environ['description']
import re

EMAIL_CHECK = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'

class RegistrationHandler(BaseHandler):
    def get(self, url):
        self.render('../static/register_activity.html')

    def post(self, url=None):
        lake = self.get_argument("lake").lower().strip()  # global/exID
        if lake == 'global':
            allowed = ('name', 'email', 'wt', 'ht', 'password')
            task = json.loads(self.get_argument("aim").strip())

            try:
                task = {i:task[i] for i in allowed}
            except KeyError:
                self.write(Api.generate_request_return(-90))
                self.finish()  
                return

            if re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', task['email']) is None\
             or (not task['wt'].is_integer())\
             or (not task['ht'].is_integer())\
             or len(task['password']) == 0: 
                self.write(Api.generate_request_return(-91))
                self.finish()
                return 

            task['opened_ex'] = (10,)
            task['valid'] = 1
            self.insert_data('users', task)
            self.write(Api.generate_request_return(1))
