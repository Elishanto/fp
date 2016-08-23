from api.baseapi import Api
from api.sysfunc import SysFunc
import datetime

systemfunctions = SysFunc(Api.database, Api)
strdate = str(datetime.datetime.now().date())
now = datetime.datetime.now()
logfile = open('learner.log', 'a+')
logfile.write(str(datetime.datetime.now()) + ' started\n')
logfile.close()
try:
    queue = Api.database['data.system'].find_one({'config': 'main'}, {'queue': 1})['queue']
    for user, exer_code in queue:
        try:
            dpush = Api.database['data.' + str(user)].find_one({'ex': exer_code}, {strdate: 1})[strdate]
        except IndexError:
            continue
        systemfunctions.fit_data(exer_code, dpush, now, user)
        Api.database['data.system'].update({'config': 'main'}, {'$pull': {'queue': (user, exer_code)}})

        logfile = open('learner.log', 'a+')
        logfile.write('{2} doing user:{0} ex:{1}'.format(user, exer_code, str(datetime.datetime.now())) + '\n')
        logfile.close()
except IndexError as e:
    logfile = open('learner.log', 'a+')
    logfile.write('error: {0}\n'.format(e))
    logfile.close()

logfile = open('learner.log', 'a+')
logfile.write(str(datetime.datetime.now()) + ' done\n')
logfile.close()
