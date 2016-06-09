import tornado.web
from pymongo import MongoClient
import bcrypt

client = MongoClient()  # базы данных


class BaseHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    database = client['health']

    def get_current_user(self):
        a = self.get_secure_cookie("user")
        if a is None:
            return None
        t = int(a.decode('utf8'))

        if self.check_via_login(t):
            return t
        else:
            pass

    def check_via_login(self, login, password):
        try:
            if self.database['users'].find_one({'id': int(login)})['valid'] == 1:
                if self.user_check_password({ 'userid':login, "check_password":password}):
                    return True
                return False #Bad password!
        except (TypeError, ValueError):
            pass
        return False

    def get_user_info(self, uid, task=None):
        if task is None:
            task = []
        if len(task) == 0:
            return self.database['users'].find_one({'id': uid})

        return self.database['users'].find_one({'id': uid}, dict(zip(task, [1] * len(task))))

    def push_data(self, identificator, path, task):
        for _ in task:
            self.database[path].update(identificator, {'$pushAll': task})

    def set_data(self, identificator, path, task):
        self.database[path].update(identificator, {'$set': task}, False, True)

    def insert_data(self, path, task):
        task['id'] = self.database[path].count() + 1
        task['valid'] = 1
        self.database[path].insert_one(task)


    def user_check_password(self, **userdata):
        tp = bytes(self.get_user_info(int(userdata['userid']), task=['password']).get('password', ''), encoding='utf8')
        """
        We need:
            * check_password
            * userid
        RETURN bool
        """
        userinfo = bytes(str(int(userdata['userid']) ** 3 % 15) + userdata['check_password'] + 'FORID' + str(
            userdata['userid']), encoding='utf8')

        return bcrypt.hashpw(userinfo, tp) == tp

    def user_process_password(self, **userdata):
        """
        We need:
            * password
            * userid
        RETURN str
        """
        return (bcrypt.hashpw(bytes(str(int(userdata['userid']) ** 3 % 15) + userdata['password'] + 'FORID' + str(
            userdata['userid']), encoding='utf8'), bcrypt.gensalt()))

    def user_setup_password(self, **userdata):
        """
        We need:
            * OLD password (if it was)
            * userid
            * new passwjrd
        RETURN bool
        """