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
        print('AA', a)
        if a is None:
            return None
        t = a.decode('utf8')

        if self.check_valid_login(t):
            return self.id_from_email(t)
        else:
            pass


    def check_valid_login(self, login):
        try:
            return(self.database['users'].find_one({'email': login})['valid'] == 1)
        except BaseException:
            return(False)

    def check_via_login(self, login, password):
        try:
            if self.database['users'].find_one({'email': login})['valid'] == 1:
                if self.user_check_password(userid=self.id_from_email(login), check_password=password):
                    return True
                print('YEP2')
                return False #Bad password!

                #TypeError, ValueError
        except (IndexError) as e:
            print('YEP4', e)
            pass

        print('YEP5')
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
        task['password'] = self.user_process_password(userid=task['id'], password=task['password'])

        self.database[path].insert_one(task)



    def id_from_email(self, uid):
        try:
            print(uid, self.database['users'].find_one({'email':uid}))
            return self.database['users'].find_one({'email':uid})['id']
        except KeyError: return False

    def user_check_password(self, **userdata):
        print('!!!user_check_password', userdata)
        tp = self.get_user_info(int(userdata['userid']), task=['password']).get('password', '')
        """
        We need:
            * check_password
            * userid
        RETURN bool
        """
        userinfo = bytes(str(userdata['userid'] ** 3 % 15) + userdata['check_password'] + 'FORID' + str(
            userdata['userid']), encoding='utf8')

        print(userinfo, tp)
        print(bcrypt.hashpw(userinfo, tp), tp)
        ans = (bcrypt.hashpw(userinfo, tp) == tp)
        return ans

    def user_process_password(self, **userdata):
        """
        We need:
            * password
            * userid
        RETURN str
        """
        salt = bcrypt.gensalt()
        print('!!!user_process_password', userdata)
        has = bcrypt.hashpw(bytes(str(userdata['userid'] ** 3 % 15) + userdata['password'] + 'FORID' + str(
            userdata['userid']), encoding='utf8'), salt)

        print('HASH', has)

        return (has)

    def initor(self, st):
        integer = len(st)
        lasts = ord(st[0])
        for i in st:
            integer = (integer + ord(i)*lasts) / 2
            lasts = ord(i)
        return(round(integer))


    def user_setup_password(self, **userdata):
        """
        We need:
            * OLD password (if it was)
            * userid
            * new passwjrd
        RETURN bool
        """