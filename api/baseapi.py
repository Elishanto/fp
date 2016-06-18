from handler import BaseHandler
import tornado




class Api(BaseHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.ALLOWED_METHODS = ['upd_file', 'upd', 'load', 'sys', 'set']


    @staticmethod
    def generate_request_return(error=-5454):
        error_description = {  # описание ошибок
            -54: "?",
            -5454: 'Undefined error',
            -10: 'Bad format',
            -504: 'Service error',
            -90: 'Wrong permissions (secure or no data)',
            1: 'Success',
            -11: 'Bad length',
            -12: 'Insufficient data',
            -13: 'The number required',
            -14: 'The number must me positive',
            -15: 'Bad extype',
            -20: 'Bad size',
            -21: 'Bad format',
            -91: 'Form inadequate',
            -100: 'Bad captcha'
        }
        try:
            return {'code': error, 'description': error_description[error]}  
        except BaseException:
            return {'code': error, 'description': error_description[-5454]}  

    def get(self):
        self.write("<script src='https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js'></script>api ;)")



    @tornado.web.authenticated
    def post(self, z=None):
        task = self.request.uri.split('/')[2].lower()
        print('TATATASK', task, self.request.body.decode(encoding='utf8'))
        if task in self.ALLOWED_METHODS:
            self.write(eval('self.api.'+task)( { i.split('=')[0]: i.split('=')[1] for i in self.request.body.decode(encoding='utf8').split('&') } ))