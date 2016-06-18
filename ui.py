import tornado.web


class Artem(tornado.web.UIModule):
    def render(self, file, **sets):
        return self.render_string("static/" + str(file), data=sets)
