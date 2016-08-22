import os
import datetime
import forecastio
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.externals import joblib
from math import sqrt


class SysFunc:
    def __init__(self, database, api):
        self.weather_cache = None
        self.api = api
        self.database = database
        self.weather_cache_time = None
        self.lat, self.lng = os.environ['lat'], os.environ['lng']
        self.formats = eval(os.environ['formats'])
        self.weather_key = os.environ['weather_key']
        self.description = os.environ['description']

    def get_weather(self, lat_, lng_, time):
        """
        Генерация метеоданных
        """
        #КЕШИРОВАНИЕ
        if True:#abs(self.api.get_user_info(self.api.get_current_user(), task = ['reg_stamp'])['reg_stamp'] - time) <= 1:
            if self.weather_cache is None:
                self.weather_cache = forecastio.load_forecast(self.weather_key, lat_, lng_,
                                                              time=datetime.datetime.now(),
                                                              units="us").hourly().data[datetime.datetime.now().hour].d
                self.weather_cache_time = datetime.datetime.now()
                return self.weather_cache
            else:
                if abs(time - self.weather_cache_time).total_seconds() // (60 * 60) <= 24:
                    return self.weather_cache

        return forecastio.load_forecast(self.weather_key, self.lat, self.lng, time=time, units="us").hourly().data[
            time.now().hour
        ].d

    def fit_data(self, extype, value, date, uid):
        """
        Обучение (и формирование) модели машинного обучения
        """
        try:
            os.makedirs('localdata/models/' + str(extype))
        except FileExistsError:
            pass

        try:
            model = joblib.load('localdata/models/{0}/{1}.pkl'.format(extype, uid))
        except FileNotFoundError:
            model = RandomForestRegressor(n_estimators=54, max_features='sqrt')

        wdata, counted = self.generate_data(extype, date, uid)

        wdata.setdefault('cloudCover', 0)
        model.fit(np.array(
            [wdata['cloudCover'], wdata['dewPoint'], wdata['humidity'], wdata['pressure'], wdata['windSpeed'],
             wdata['temperature'], wdata['windBearing'], counted[0], counted[1], counted[2], counted[3],
             counted[4]]).reshape(1, -1), [value])
        joblib.dump(model, 'localdata/models/{0}/{1}.pkl'.format(extype, uid))

    def generate_data(self, extype, date, uid):
        """
        Функция генерации данных для обучения и работы с моделью
        """
        wdata = self.get_weather(self.lat, self.lng, date)  # получение данных погоды
        rk = self.database['data_{0}'.format(uid)].find_one({'ex': int(extype)},
                                                            {'_id': 0, 'ex': 0})  # учёт статистических данных
        zx = sorted(rk.keys())[-5:]
        rk = [rk[i] for i in zx]

        counted = []
        for key, wdate in enumerate(zx):

            delta = abs(datetime.datetime.now().date() - datetime.timedelta(days=int(wdate)) -
                        datetime.datetime.now().date()).total_seconds() / (60 * 60 * 24)  # учёт временного интервала
            counted.append(sqrt(rk[key]) / 2 ** delta)

        return wdata, counted

    def predict_data(self, extype, date, uid, period=1, utp_coef=1.05):
        """
        Функция прогноза последующего выполнении на основе машинного обучения
        """
        model = joblib.load('localdata/models/{0}/{1}.pkl'.format(extype, uid))  # открытие существующей модели
        if period <= 1:  # period - длительность необходимого прогноза
            wdata, counted = self.generate_data(extype, date, uid)
            return (round(model.predict(np.array([wdata['cloudCover'], wdata['dewPoint'],
                                                  wdata['humidity'], wdata['pressure'], wdata['windSpeed'],
                                                  wdata['temperature'],
                                                  wdata['windBearing'], counted[0], counted[1], counted[2], counted[3],
                                                  counted[4]])
                                        .reshape(1, -1))[0] * utp_coef))  # использование модели
        result = []
        wdata, counted_base = self.generate_data(extype, date, uid)

        for i in range(period):
            counted = [sqrt(val) / 2 ** (len(counted_base) - rs - 1) for rs, val in enumerate(counted_base)]
            rpdict = round(model.predict(np.array([wdata['cloudCover'], wdata['dewPoint'], wdata['humidity'],
                                                   wdata['pressure'], wdata['windSpeed'], wdata['temperature'],
                                                   wdata['windBearing'], counted[0],
                                                   counted[1], counted[2], counted[3], counted[4]])
                                         .reshape(1, -1))[0] * utp_coef ** i)  # использование модели
            result.append(rpdict)
            counted_base.append(rpdict)

        return result

    def plan(self, uid, extype, pediod=5):
        """
        Функция генерации истории, базового и физического планов, общей программы
        """
        # plnday = self.database['data_{0}'.format(uid)]['stat'].find_one({'ex': extype}, {'_count': 1})['_count']  # учёт статистики
        rk = []
        datess = []

        try:
            future = self.predict_data(extype, datetime.datetime.now(), uid, period=pediod)
        except IndexError:
            return Api.generate_request_return(-12)
        plan = []

        try:
            idol = self.database['data_{0}'.format(uid)]['stat'].find_one({'ex': extype}, {'before': 1})['before']
        except KeyError:
            idol = round(self.database['data_{0}'.format(uid)]['stat'].find_one({'ex': extype}, {'_all': 1})
                         ['_all'] /
                         self.database['data_{0}'.format(uid)]['stat'].find_one({'ex': extype}, {'_count': 1})
                         ['_count'], 1)
            self.database['data_{0}'.format(uid)]['stat'].update({'ex': extype}, {'$set': {'before': idol}})

        program = []
        for dlt in range(pediod):
            plan.append(self.calculate_default_program(uid, idol, extype, dlt))
            program.append(int(sqrt((plan[-1] * future[dlt]))))

            daytofind = (datetime.datetime.now() - self.get_user_info(uid, task=['reg_stamp'])['reg_stamp']).days()
            try:
                n = self.database['data_{0}'.format(uid)].find_one({'ex': extype}, {daytofind: 1})[daytofind]
            except KeyError:
                n = 0
            rk.append(n)
            datess.append(str(daytofind.date()))

        return {'old': rk, 'old_date': datess, 'future': future, 'plan': plan, 'program': program}

    def get_user_url(self, user):
        """
        Получение аватара
        """
        try:
            n = self.database['users'].find_one({'id': user}, {'imgurl': 1})['imgurl']
        except KeyError:
            return '/files/users/default.png'

        return '/files/users/' + str(n)


    def calculate_default_program(self, user, now, exer_code, plus):
        """
        Расчёт базового плана
        """
        x = plus + self.database['data_{0}'.format(user)]['stat'].find_one({'ex': exer_code}, {'_count': 1})['_count']
        strategy = 1  # (0)-Постепенно закрепить, (1)-Быстро преумножить
        goal = now * 1.1  # Не может быть меньше, чем сейчас

        if strategy == 0:
            if (goal - now) / now > 0.5:
                # режим больших услилий
                # hard_work_days = 5
                zoom = '*1,*1.25,*1.3,*1.30,*1.45,*1.2,*1.1,*1.1'.split(',')

            else:
                # режим постепенного закрепления
                # hard_work_days = 4
                zoom = '*1,+1,*1.1,*1.5,+4,*1.2,*1.4,*1.1'.split(',')
        else:
            if (goal - now) / now > 0.7:
                # режим наибольшей временной продуктисности
                # hard_work_days = 3
                zoom = '*1,*1.4,+1,*1.3,+2,*1.2,+1,*1.1'.split(',')

            else:
                # пассивный режим преумножения
                # hard_work_days = 2
                zoom = '*1,*1.25, +1, +2 ,+3, +1,*0.9,+3'.split(',')

        for i in range((x + 1) // 7):
            now = int(eval(str(now) + zoom[-1]))

        return int(eval(str(now) + zoom[(x + 1) % 7]))  # умножение

    def get_user_grop(self, uid):
        """

        """
        data = self.get_user_info(uid, task=['wt', 'ht'])
        coef = data['wt']/data['ht']
        GROUPS = [2.5, 3, 1, 10] #!

        nn = [abs(coef-i) for i in GROUPS]
        nn = [ i/sum(nn) for i in nn ]

        return nn




    def upd_data(self, uid, exer_code, count, day_before):
        """
        1) поднять в архивах историю пользователя за все дни до этого.
        2) понять, насколько она отличается от значения стастистики, которое есть у нас
        3) посчитать среднее арифметическое квадрата разницы оф. данных и истории юзера
        4) обновить программу как
           a*b + c*d, где a+b=1 и a является коэф. по обратной пропорции, b - результату пользователя (count), с - 1-a, d - официальным данным за этот период

        архивы поднимать по группе, к которой принадлежит пользователь
        """

        
        try:
            beforeprogramm = self.database['data.system.beforeprogram'].find_one({'exer_code':exer_code, 'group':self.get_user_grop(uid)})['uppers']
        except KeyError:
            beforeprogram = []

        beforeprogram = beforeprogram + [0 for i in range(max(0, day_before - len(beforeprogram) ))]
        usr_data = self.database['data.'+str(uid)].find_one()
        error  = 0

        for i in range(day_before):
            try:
                usr_ans = usr_data[str(i)]
            except BaseException:
                usr_ans = 0

            error += (beforeprogram[i] - usr_ans) ** 2

        print(error)