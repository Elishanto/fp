import tornado.web
from pymongo import MongoClient
import bcrypt

client = MongoClient()  # базы данных
import api.sysfunc
import os
import datetime
import imghdr
import json
import tornado




class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.data = {"exer": (10, 11, 54, 777, 6698, 778, 12, 13)}  # общедоступные упражнения
        self.lat, self.ng = os.environ['lat'], os.environ['lng']
        self.formats = eval(os.environ['formats'])
        self.weather_key = os.environ['weather_key']
        self.description = os.environ['description']
    
    database = client['health']

    def data_received(self, chunk):
        pass
    
    def get_current_user(self):
        a = self.get_secure_cookie("user")
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
                return False #Bad password!

                #TypeError, ValueError
        except (IndexError) as e:
            pass

        return False

    def get_user_info(self, uid, task=[]):
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
            return self.database['users'].find_one({'email':uid})['id']
        except KeyError: return False

    def user_check_password(self, **userdata):
        tp = self.get_user_info(int(userdata['userid']), task=['password']).get('password', '')
        """
        We need:
            * check_password
            * userid
        RETURN bool
        """
        userinfo = bytes(str(userdata['userid'] ** 3 % 15) + userdata['check_password'] + 'FORID' + str(
            userdata['userid']), encoding='utf8')

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
        has = bcrypt.hashpw(bytes(str(userdata['userid'] ** 3 % 15) + userdata['password'] + 'FORID' + str(
            userdata['userid']), encoding='utf8'), salt)


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


    def upd_file(self, fl, taskfile='avatar'):
        if taskfile == 'avatar':
            avatar = fl
            ftype = imghdr.what(None, avatar)
            user = self.get_current_user()

            if len(avatar) > 540000:
                return(self.generate_request_return(-20))
            elif ftype not in self.formats:
                return(self.generate_request_return(-21))
            else:

                for i in self.formats:
                    try:
                        os.remove('static/files/users/{0}.{1}'.format(user, i))
                    except FileNotFoundError:
                        pass
                fu = open('static/files/users/{0}.{1}'.format(user, ftype), 'wb+')

                self.set_data({'id': int(self.get_current_user())}, 'users',
                              {'imgurl': '{0}.{1}'.format(user, ftype)})

                fu.write(avatar)
                fu.close()

                return(self.generate_request_return(1))


    def upd(self, args):
        jtype = args.get('type').lower().strip()
        if jtype == 'push_excer':
            exer_code = int(args.get("exer_code"))
            if int(exer_code) in self.data['exer']:
                try:
                    dpush = int(args.get("data"))
                except ValueError:
                    return(self.generate_request_return(-13))

                if dpush <= 0:
                    return(self.generate_request_return(-14))

                self.database['data.{0}'.format(self.get_current_user())].update(
                    {'ex': exer_code},
                    {'$inc': {str(datetime.datetime.now().date()): dpush}}, upsert=True)
                self.database['data.{0}'.format(self.get_current_user())]['stat'].update(
                    {'ex': exer_code},
                    {'$inc': {'_all': dpush, '_count': 1}})
                self.database['data.system'].update(
                    {'config': 'main'}, {'$addToSet': {'queue': (self.get_current_user(), exer_code)}})
                return({'code': 1})
            else:
                return(self.generate_request_return(-15))

        elif jtype == 'takedata':
            # получнеие данных
            exer_code = int(args.get("exer_code"))
            if int(exer_code) in self.data['exer']:
                predval = api.sysfunc.SysFunc(self.database, self).predict_data(exer_code, datetime.datetime.now(),
                                                       self.get_current_user())
                plnday = self.database['data.{0}'.format(self.get_current_user())]['stat'].find_one(
                    {'ex': exer_code}, {'_count': 1})['_count']
                program = round((plnday % 30 + 5 + predval) / 2)
                try:
                    srv = self.database['data.{0}'.format(self.get_current_user())].find_one(
                        {'ex': exer_code}, {str(datetime.datetime.now().date()): 1})[
                        str(datetime.datetime.now().date())]
                except KeyError:
                    srv = 0

                return({'code': 1, 'predval': predval, 'srv': srv, 'program': program})

        elif jtype == 'plan':
            # МЕТОД API: работа с планом
            exer_code = int(args.get("exer_code"))
            if int(exer_code) in self.data['exer']:
                return(api.sysfunc.SysFunc(self.database, self).plan(self.get_current_user(), exer_code))


        else:
            try:
                return(self.generate_request_return())
            except BaseException:
                pass


    def load(self,  args):
        agr = args.get('aim').lower().strip()
        if agr == 'basic':
            user = self.get_current_user()
            return(self.get_user_info(user, ['name', 'email', 'wt', 'ht']))

    def sys(self, args):
        task = args.get('task').strip()

        if task == 'check_firstrun':
            exer_code = int(args.get("exer_code").lower().strip())
            if self.database['data.{0}'.format(self.get_current_user())]['stat'].find_one(
                    {'ex': exer_code}) is None:
                return({'code': 0})
            else:
                return(self.generate_request_return())
        elif task == 'ex_opened':
            response = {'code': 1,
                        'opened_ex': self.get_user_info(self.get_current_user(), ['opened_ex'])['opened_ex']}
            return(response)

        elif task == 'ex_description':
            return({'code': 1, 'description': description})

        elif task == 'repair_firstrun':
            exer_code = int(args.get("exer_code").lower().strip())
            pushdata = [int(i) for i in args.get("data").lower().strip().split(';')]
            if len(pushdata) != 5:
                return(self.generate_request_return(-11))
            sa = 0
            for i in range(1, 6):
                day = datetime.datetime.now() - datetime.timedelta(days=i)
                ndone = pushdata[i - 1]
                sa += ndone
                self.database['data.{0}.stat'.format(self.get_current_user())].update({'ex': exer_code}, {
                    '$inc': {'_all': ndone, '_count': 1}}, upsert=True)
                self.database['data.{0}'.format(self.get_current_user())].update({'ex': exer_code}, {
                    '$inc': {str(day.date()): ndone}}, upsert=True)

            for i in range(1, 6):
                day = datetime.datetime.now() - datetime.timedelta(days=i)
                ndone = pushdata[i - 1]
                api.sysfunc.SysFunc(self.database, self).fit_data(exer_code, ndone, day, self.get_current_user())

            self.database['data.{0}.stat'.format(self.get_current_user())].update({'ex': exer_code},
                                                                                  {'$set': {'before': sa // 5}})
            return(self.generate_request_return(1))

    def set(self, args):
        # МЕТОД API: установка пользовательской информации
        lake = args.get('lake').lower().strip()  # global/exID
        if lake == 'global':
            allowed = ('name', 'email', 'wt', 'ht')
            task = json.loads(args.get("aim").strip())
            for i in task.keys():
                if i not in allowed:
                    return(self.generate_request_return(-90))
            self.set_data({'id': int(self.get_current_user())}, 'users', task)
            return(self.generate_request_return(1))