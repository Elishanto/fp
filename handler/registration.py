import json
import os
from handler import BaseHandler
from api.baseapi import Api
import re
import recaptcha2
import datetime
description = os.environ['description']

EMAIL_CHECK = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'
CAPTCHA_SECRET_KEY = '6LdadiITAAAAAI0o59pEnTCHGCn5Zh4bB17PJ-bt'


class RegistrationHandler(BaseHandler):
    def get(self, url):
        self.render('../static/register_activity.html')

    def post(self, url=None):
        lake = self.get_argument("lake").lower().strip()  # global/exID
        if lake == 'global':
            allowed = ('name', 'email', 'wt', 'ht', 'password')
            task = json.loads(self.get_argument("aim").strip())

            # if not ('captcha' not in task.keys() or
            #             recaptcha2.verify(CAPTCHA_SECRET_KEY, task['captcha'], self.request.remote_ip)['success']):
            #     self.write(Api.generate_request_return(-100))
            #     self.finish()
            #     return

            try:
                task = {i: task[i] for i in allowed}
            except KeyError:
                self.write(Api.generate_request_return(-90))
                self.finish()
                return

            if re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', task['email']) is None \
                    or (not task['wt'].isdigit()) \
                    or (not task['ht'].isdigit()) \
                    or len(task['password']) == 0:
                self.write(Api.generate_request_return(-91))
                self.finish()
                return

            task['reg_stamp'] = datetime.datetime.now()
            task['opened_ex'] = (10,)
            task['valid'] = 1
            self.insert_data('users', task)
            self.write(Api.generate_request_return(1))