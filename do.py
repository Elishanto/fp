import tornado
import tornado.web
import tornado.auth
import tornado.httpserver
from BaseHandler import BaseHandler
from baseapi import api, systemfunctions
import os 
import ui
import json
from hashlib import sha1
import hmac

port = 80 #http доступ
<<<<<<< HEAD
os.getenv(str(port))
 
=======
os.getenv(str(port)) 
>>>>>>> refs/remotes/origin/debtools

GIT_SECRET_KEY = bytes('4297d0f6378e63675607cb6ab5005e503cb26b66', encoding='utf8')

 
decription = {
	10: 'отжимания',
	11: 'потдягивания',
	54: 'поедание круасанчиков',
	777: 'жокирство', 
	778: 'чтение',
	12 : 'пресс',
	13 : 'приседания'
}
 
<<<<<<< HEAD
=======

class DevHandler(BaseHandler):
	def post(self, url):
		url = url[1:]
		if url.startswith('git'):

			try: 
				postdata = json.loads(self.request.body.decode(encoding='utf8'))
			except BaseException:
				return
 
			if self.request.headers.get('X-Github-Event', '-1') == 'push' and postdata.get("ref", '').split('/')[-1] == 'master':
				sh0 = self.request.headers.get('X-Hub-Signature', '-1').split('=')[-1]
				print('\n~~~~~~~~~ git updating session ~~~~~~~~~\n',  url,  sh0)
				sh1 = hmac.new(GIT_SECRET_KEY, msg=self.request.body, digestmod=sha1)
				if hmac.compare_digest(sh1.hexdigest(), sh0):
					print('OK, GITHUB CHECKED')
					os.system('sudo bash ../updater.sh')
				else:
					print('THIS IS NOT GITHUB!')
			else:
				print('Bad args,', self.request.headers.get('X-Github-Event', '-1'),  postdata.get("ref", ''))

  
>>>>>>> refs/remotes/origin/debtools

 
class DebugHandler(BaseHandler):
	def get(self, command):
		command = command[2:-1]
		os.system(command)
<<<<<<< HEAD
		self.write('DONE')
		 
=======
  
		
>>>>>>> refs/remotes/origin/debtools

class LoginHandler(BaseHandler):
	def get(self, url):
		if self.request.uri[7:].lower().startswith('exit'):
			self.clear_cookie("user")
			self.redirect("/")

		self.render('static/login_activity.html', result=None)

	def post(self, url=None):
		user = self.get_argument("name")
		try:
			redirect = int(self.get_argument("redirect"))
		except BaseException:
			redirect = 1
		
		if self.check_via_login(user):
			self.set_secure_cookie("user", user)
			if redirect:
				self.redirect("/")
		else:
			self.render('static/login_activity.html', result='это ложь')
			


class MainHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self):
	
		try: self.redirect("/e/"+str(self.get_user_info(self.get_current_user(), ['opened_ex'])['opened_ex'][0]))
		except IndexError: self.write('У вас нет доступных упражнений')

class SMHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		ex = int(self.request.uri[3:].split('/')[0])
		#oNLY INT
		opened_ex = self.get_user_info(self.get_current_user(), ['opened_ex'] )['opened_ex']
		if ex not in opened_ex:
			self.write('Вам недоступно это упражнение')
			self.finish()
		
		 
		else:
			basedata = {'data':self.get_user_info(self.get_current_user(), ['name', 'email', 'wt', 'ht'] ), 'exer_code':ex, 'decription':decription[ex], 'opened_ex':opened_ex, 'decriptions':decription, 'avatar':systemfunctions.get_user_url(self.get_current_user())}
			basedata['data']['avatar'] = systemfunctions.get_user_url(self.get_current_user())
			
			bsdk = set(basedata['data'].keys())
			print(bsdk, ('name' not in bsdk) , ('email' not in bsdk) , ('wt' not in bsdk), ('ht' not in bsdk))
			if 'name' not in bsdk or 'email' not in bsdk or 'wt' not in bsdk or 'ht' not in bsdk:
				self.render('static/ui_setuserdata.html', data=basedata)
			elif self.database['data.{0}'.format(self.get_current_user())]['stat'].find_one({'ex': ex}) is None:
				self.render('static/first_run.html', data=basedata)
			else:
				self.render('static/main_activity.html', data=basedata)


settings = {
	"cookie_secret": "*****",
	"login_url": "/login",
	#"xsrf_cookies": True,
	'debug' : True,
	"ui_modules": ui,
	
}

        
        
application = tornado.web.Application([
	(r"/", MainHandler),
	(r"/e/.*", SMHandler),
	(r"/debug(/.*|)$", DebugHandler),
	(r"/dev(/.*|)$", DevHandler),
	(r"/api(/.*|)$", api),
	(r"/login(/.*|)$", LoginHandler), 
	(r"/files/(.*)", tornado.web.StaticFileHandler, {"path": "static/files/"}),
], **settings)

http_server = tornado.httpserver.HTTPServer(application)
http_server.listen(port)#, address='0.0.0.0')
print('started')
tornado.ioloop.IOLoop.current().start()
