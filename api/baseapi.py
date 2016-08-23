from handler import BaseHandler
import tornado


class Api(BaseHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.ALLOWED_METHODS = ['upd_file', 'upd', 'load', 'sys', 'set']

    def get(self):
        self.write("<script src='https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js'></script>api ;)")

    @tornado.web.authenticated
    def post(self, _=None):
        task = self.request.uri.split('/')[2].lower()
        print('TATATASK', task, self.request.body.decode(encoding='utf8'))
        if task in self.ALLOWED_METHODS:
            self.write(eval('self.' + task)({i.split('=')[0]: i.split('=')[1] for i in
                                             self.request.body.decode(encoding='utf8').split('&')
                                             }))
