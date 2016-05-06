import tornado
import tornado.web
import tornado.auth
from pymongo import MongoClient
client = MongoClient() #базы данных

class BaseHandler(tornado.web.RequestHandler):
	database = client['health']
	
	def get_current_user(self):
		a = self.get_secure_cookie("user")
		if a is None: return(None)
		t = int(a.decode('utf8'))
	
		if self.check_via_login(t):
			return(t)
		else:
			print('пользователь удалён')

	def check_via_login(self, login):
		try:
			if self.database['users'].find_one({'id':int(login)})['valid'] == 1:
				return(True)
		except (TypeError, ValueError) : pass
		return(False)


	def get_user_info(self, uid, task=[]):
		anser = {}
		print('\t get', uid, task)
		if len(task) == 0: 
			print('\return', self.database['users'].find_one({'id':uid}), '\n')
			return(self.database['users'].find_one({'id':uid}))
		
		print('\t return', self.database['users'].find_one({'id':uid}, dict(zip(task, [1]*len(task)))), '\n')
		return(self.database['users'].find_one({'id':uid}, dict(zip(task, [1]*len(task)))))


	def push_data(self, indificator, path, task):
		for i in task:
			self.database[path].update(indificator, {'$pushAll': task})


	def set_data(self, indificator, path, task):
		print(task, path, indificator, task)
		self.database[path].update(indificator, {'$set': task}, False, True)

