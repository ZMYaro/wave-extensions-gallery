#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import os

from google.appengine.api import users
from google.appengine.dist import use_library
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from datastore import User

use_library('django', '1.2')

class AccountPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
			self.response.out.write(template.render(path, {'title':'Your Account'}))
			path = os.path.join(os.path.dirname(__file__), 'templates/account.html')
			self.response.out.write(template.render(path, {}))
			path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
			self.response.out.write(template.render(path, {}))
		else:
			self.redirect(users.create_login_url(self.request.uri))

class StarAdder(webapp.RequestHandler):
	def get(self, extID):
		user = users.get_current_user()
		if user:
			userEntry = User.gql('WHERE user = :1',user).get()
			if not userEntry:
				userEntry = User()
				userEntry.user = user
				userEntry.starred = []
			userEntry.starred.append(extID)
			userEntry.put()
		else:
			self.redirect(users.create_login_url(self.request.uri))

class StarAdder(webapp.RequestHandler):
	def get(self, extID):
		user = users.get_current_user()
		if user:
			userEntry = User.gql('WHERE user = :1',user).get()
			if not userEntry:
				userEntry = User()
				userEntry.user = user
				userEntry.starred = []
			userEntry.starred.append(extID)
			userEntry.put()
			self.redirect('/gallery/info/' + extID)
		else:
			self.redirect(users.create_login_url(self.request.uri))

class StarRemover(webapp.RequestHandler):
	def get(self, extID):
		user = users.get_current_user()
		if user:
			userEntry = User.gql('WHERE user = :1',user).get()
			if not userEntry:
				userEntry = User()
				userEntry.user = user
				userEntry.starred = []
			if extID in userEntry.starred:
				userEntry.starred.remove(extID)
			userEntry.put()
			self.redirect('/gallery/info/' + extID)
		else:
			self.redirect(users.create_login_url(self.request.uri))

class OtherPage(webapp.RequestHandler):
	def get(self, page):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {'title':'Error'}))
		path = os.path.join(os.path.dirname(__file__), 'templates/404.html')
		self.response.out.write(template.render(path, {}))
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))
		self.response.set_status(404);

site = webapp.WSGIApplication([('/account', AccountPage),
                               ('/account/star/(\w{16})', StarAdder),
                               ('/account/unstar/(\w{16})', StarRemover),
                               ('/(.*)', OtherPage)],
                              debug=True)

def main():
	run_wsgi_app(site)

if __name__ == '__main__':
	main()
