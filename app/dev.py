#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import hashlib
import os

from google.appengine.api import users
from google.appengine.dist import use_library
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from datastore import Extension

use_library('django', '1.2')

class DevDash(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
			self.response.out.write(template.render(path, {'title':'Developer Dashboard'}))
			
			extlist = Extension.gql('WHERE developer = :1',user).fetch(None)
			path = os.path.join(os.path.dirname(__file__), 'templates/devdash.html')
			self.response.out.write(template.render(path, {'extlist':extlist}))
			
			path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
			self.response.out.write(template.render(path, {}))
		else:
			self.redirect(users.create_login_url(self.request.uri))

class NewExt(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			# Create a new Extension entry
			newExt = Extension()
			newExt.developer = user
			
			# Give the Extension a random unique ID (I decided on 16 hexadecimal
			# characters, but other suggestions are welcome)
			newExt.extID = hashlib.md5(os.urandom(128)).hexdigest()[:16]
			while Extension.gql('WHERE extID = :1', newExt.extID).count(limit=2) > 0:
				newExt.extID = hashlib.md5(os.urandom(128)).hexdigest()[:16]
			newExt.put()
		
			# Redirect to the editing page
			self.redirect('/dev/edit/' + newExt.extID)
		else:
			self.redirect(users.create_login_url(self.request.uri))

class EditExt(webapp.RequestHandler):
	def get(self,extID):
		user = users.get_current_user()
		if user:
			path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
			self.response.out.write(template.render(path, {'title':'Edit Extension'}))
			
			ext = Extension.gql('WHERE extID = :1', extID).get()
			if ext:
				if ext.developer == user:
					path = os.path.join(os.path.dirname(__file__), 'templates/edit.html')
					self.response.out.write(template.render(path, {'ext':ext}))
				else:
					self.response.out.write('<h1>Error</h1>')
					self.response.out.write('<p>You do not have permission to edit this extension.</p>')
					self.response.out.write('<p><a href=\"/dev\">Click here</a> to return to your developer dashboard.</p>')
			else:
				self.response.out.write('<h1>Error</h1>')
				self.response.out.write('<p>Extension ' + extID + ' could not be found.</p>')
				self.response.out.write('<p><a href=\"/dev\">Click here</a> to return to your developer dashboard.</p>')
			
			path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
			self.response.out.write(template.render(path, {}))
		else:
			self.redirect(users.create_login_url(self.request.uri))
	def post(self,extID):
		user = users.get_current_user()
		if user:
			ext = Extension.gql('WHERE extID = :1', extID).get()
			if ext and ext.developer == user:
				if self.request.get('title'):
					ext.title = self.request.get('title')
				if self.request.get('type'):
					ext.type = self.request.get('type')
				if self.request.get('description'):
					ext.description = self.request.get('description')
				ext.put()
				self.redirect('/dev')
				return
		self.redirect('/dev/edit/' + extID)

class OtherPage(webapp.RequestHandler):
	def get(self,page):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {'title':'Error'}))
		path = os.path.join(os.path.dirname(__file__), 'templates/404.html')
		self.response.out.write(template.render(path, {}))
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))
		self.response.set_status(404);


site = webapp.WSGIApplication([('/dev/new/?', NewExt),
                               ('/dev/edit/(\w{16})/?', EditExt),
                               ('/dev/?', DevDash),
                               ('/(.*)', OtherPage)],
                              debug=True)

def main():
	run_wsgi_app(site)

if __name__ == '__main__':
	main()
