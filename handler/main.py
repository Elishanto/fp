import tornado
from handler import BaseHandler


class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        try:
            self.redirect("/e/" + str(self.get_user_info(self.get_current_user(), ['opened_ex'])['opened_ex'][0]))
        except IndexError:
            self.write('У вас нет доступных упражнений')
