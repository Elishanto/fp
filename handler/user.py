from handler import BaseHandler

available = ['register', 'baseinfo']


class UserHandler(BaseHandler):
    def get(self, url):
        action = url.split('/')
        now = action[0]

        if now in available:
            eval('self.' + now(action[1:]))
        else:
            self.write('Задача неопознана')

    def register(self, url):
        referal = self.get_argument("ref", '', True)
        self.render('../static/register_activity.html', referal=referal)

    def baseinfo(self, url):
        """Взять базовую инфу о пользователе через BaseHandler.get_user_info
        ... и вывести имя, фамилию, вес, программу и пр
        И сделать доступным редактирование параметров (метод api SET — смотри JS функцию upload_sysinfo)
        """
