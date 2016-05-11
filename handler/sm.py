import os
import tornado
from handler import BaseHandler
from api.sysfunc import SysFunc
from api.baseapi import Api

print(vars())

description = os.environ['description']


class SMHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        ex = int(self.request.uri[3:].split('/')[0])
        # oNLY INT
        opened_ex = self.get_user_info(self.get_current_user(), ['opened_ex'])['opened_ex']
        if ex not in opened_ex:
            self.write('Вам недоступно это упражнение')
            self.finish()
        else:
            basedata = {'data': self.get_user_info(self.get_current_user(), ['name', 'email', 'wt', 'ht']),
                        'exer_code': ex, 'description': description[ex], 'opened_ex': opened_ex,
                        'descriptions': description, 'avatar': SysFunc(Api.database).get_user_url(self.get_current_user())}
            basedata['data']['avatar'] = SysFunc(Api.database).get_user_url(self.get_current_user())

            bsdk = set(basedata['data'].keys())
            if 'name' not in bsdk or 'email' not in bsdk or 'wt' not in bsdk or 'ht' not in bsdk:
                self.render('static/ui_setuserdata.html', data=basedata)
            elif self.database['data.{0}'.format(self.get_current_user())]['stat'].find_one({'ex': ex}) is None:
                self.render('static/first_run.html', data=basedata)
            else:
                self.render('static/main_activity.html', data=basedata)
