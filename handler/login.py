from handler import BaseHandler


class LoginHandler(BaseHandler):
    def get(self, url):
        if self.request.uri[7:].lower().startswith('exit'):
            self.clear_cookie("user")
            self.redirect("/")

        self.render('../static/login_activity.html', result=None)

    def post(self, url=None):
        try:
            user = self.get_argument("email")
            try:
                redirect = int(self.get_argument("redirect"))
            except BaseException:
                redirect = 1

            if self.check_via_login(user, self.get_argument("pass")):
                self.set_secure_cookie("user", user)
                if redirect:
                    self.redirect("/")
            else:
                self.render('../static/login_activity.html', result='это ложь')
        except BaseException:
            self.redirect("/")