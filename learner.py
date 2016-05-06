import api
import datetime
systemfunctions = api.fn()
strdate = str(datetime.datetime.now().date())
now = datetime.datetime.now()
logfile = open('learner.log', 'a+')
logfile.write(str(datetime.datetime.now())+' started\n')
logfile.close()
try:
    queue = api.api.database['data.system'].find_one({'config':'main'}, {'queue':1})['queue']
    for user, exer_code in queue:
        try: dpush = api.api.database['data.'+str(user)].find_one({'ex':exer_code}, {strdate:1})[strdate]
        except IndexError: continue
        systemfunctions.fitdata(exer_code, dpush, now, user)
        api.api.database['data.system'].update({'config':'main'}, {'$pull':{'queue': (user, exer_code)}})
        
        logfile = open('learner.log', 'a+')
        logfile.write('{2} doing user:{0} ex:{1}'.format(user, exer_code, str(datetime.datetime.now()))+'\n')
        logfile.close()
except IndexError as e:
    logfile = open('learner.log', 'a+')
    logfile.write('error: {0}\n'.format(e))
    logfile.close()

logfile = open('learner.log', 'a+')
logfile.write(str(datetime.datetime.now())+ ' done\n')
logfile.close()