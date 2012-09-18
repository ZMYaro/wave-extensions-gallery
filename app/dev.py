#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import hashlib
import os

from google.appengine.api import images
from google.appengine.api import users
from google.appengine.dist import use_library
from google.appengine.ext import db
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
			
			extlist = Extension.gql('WHERE developer = :1 ORDER BY title ASC', user).fetch(None)
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
			templateArgs = {'title':'Edit Extension'}
			if self.request.get('msg'):
				if self.request.get('msg') == 'success':
					templateArgs['message'] = 'Your extension has been successfully updated.'
				elif self.request.get('msg') == 'icontype':
					templateArgs['message'] = 'The icon you uploaded was not a PNG.  Your extension\'s other properties have been successfully updated.'
				templateArgs['message'] += '  <a href=\"/dev\">Click here</a> to return to the developer dashboard.</a>'
			path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
			self.response.out.write(template.render(path, templateArgs))
			
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
			error = None
			ext = Extension.gql('WHERE extID = :1', extID).get()
			if ext and ext.developer == user:
				if self.request.get('title'):
					ext.title = self.request.get('title')
				
				if self.request.get('type'):
					ext.type = self.request.get('type')
				else: # default to gadget if no type is sent
					ext.type = 'gadget'
				
				if self.request.get('description'):
					ext.description = self.request.get('description')
				
				if self.request.get('icon'):
					iconFile = self.request.get('icon')
					icon = images.Image(image_data = iconFile)
					if icon.format != images.PNG:
						error = 'icontype'
					else:
						iconFile = images.resize(iconFile, 128, 128)
						ext.icon = db.Blob(iconFile)
				
				ext.put()
				
				if error == None:
					self.redirect('/dev/edit/' + extID + '?msg=success')
				else:
					self.redirect('/dev/edit/' + extID + '?msg=' + error)
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

# quickly adds some extensions to the gallery
class QuickAdder(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			if user.email() != 'zmyaro@gmail.com':
				self.response.out.write('Not allowed.')
				return
			exts = [
				{
					'title':'Time Zone Gadget (Beta)',
					'type':'gadget',
					'description':'Displays a set date and time in each user\'s own time zone.  Useful for planning an event involving people from different time zones.',
					'gadgetURL':'http://mysite.verizon.net/zmyaro/projects/wave/gadgets/time_zone.xml'
				},
				{
					'title':'Yes/No/Mini Gadget',
					'type':'gadget',
					'description':'A miniature version of Google\'s Yes/No/Maybe Gadget.  Like the Yes/No/Maybe gadget, just click one of the buttons to vote.',
					'gadgetURL':'http://mysite.verizon.net/zmyaro/projects/wave/gadgets/ynmini.xml'
				},
				{
					'title':'Googley Like Button',
					'type':'gadget',
					'description':'A like button designed to look like those in Google Reader and Google Buzz.',
					'gadgetURL':'http://mysite.verizon.net/zmyaro/projects/wave/gadgets/like.xml'
				},
				{
					'title':'Petition Gadget (Beta)',
					'type':'gadget',
					'description':'A gadget that allows you to do petitions in Wave. Some advantages of this are that people can see the petition text being written in real-time and a signer\'s name and picture can be retrieved from the his/her wave profile, so the he/she does not have to enter it manually.',
					'gadgetURL':'http://mysite.verizon.net/zmyaro/projects/wave/gadgets/petition.xml'
				}
			]
			for ext in exts:
				extEntity = Extension()
				extEntity.developer = user
				for prop in ext:
					setattr(extEntity, prop, ext[prop])
				extEntity.put()
			self.response.out.write('Four extensions have been added to the gallery.')
		else:
			self.redirect(users.create_login_url(self.request.uri))

site = webapp.WSGIApplication([('/dev/new/?', NewExt),
                               ('/dev/edit/(\w{16})/?', EditExt),
                               ('/dev/?', DevDash),
                               ('/dev/quickadd', QuickAdder),
                               ('/(.*)', OtherPage)],
                              debug=True)

def main():
	run_wsgi_app(site)

if __name__ == '__main__':
	main()
