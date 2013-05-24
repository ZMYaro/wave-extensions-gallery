#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import hashlib
import os
import re

from google.appengine.api import images
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from constants import *
from datastore import Extension,Rating

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
			# characters, but other suggestions are welcome).
			newExt.extID = hashlib.md5(os.urandom(128)).hexdigest()[:16]
			while Extension.gql('WHERE extID = :1', newExt.extID).count(limit=1) > 0:
				newExt.extID = hashlib.md5(os.urandom(128)).hexdigest()[:16]
			newExt.put()
			
			# Automatically upvote the extension as the developer
			
			# Check if a rating for that extension ID exists
			# (it should not, but just in case).
			rating = Rating.gql('WHERE user = :1 AND extID = :2',user,newExt.extID).get()
			# Create the rating if it does not exist
			# (which, again, it should not).
			if not rating:
				rating = Rating()
				rating.user = user
				rating.extID = newExt.extID
			rating.value = 1
			rating.put()
			
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
					templateArgs['message'] = 'Your extension has been successfully updated.   You can stay here, <a href=\"/gallery/info/' + extID + '\">see your extension in the gallery</a>, or '
				elif self.request.get('msg') == 'icontype':
					templateArgs['message'] = 'The icon you uploaded was not a PNG.  Your extension\'s other properties have been successfully updated.  You can stay here or '
				elif self.request.get('msg') == 'screenshottype':
					templateArgs['message'] = 'One or more of the screenshots you uploaded was not a PNG.  Your extension\'s other properties have been successfully updated.  You can stay here or '
				elif self.request.get('msg') == 'badurl':
					templateArgs['message'] = 'The gadget URL you entered was improperly formatted and therefore not saved.  Your extension\'s other properties have been successfully updated.  You can stay here or '
				elif self.request.get('msg') == 'badaddress':
					templateArgs['message'] = 'The address you entered was improperly formatted and therefore not saved.  Your extension\'s other properties have been successfully updated.  You can stay here or '
				templateArgs['message'] += '<a href=\"/dev\">return to your developer dashboard.</a>'
			path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
			self.response.out.write(template.render(path, templateArgs))
			
			ext = Extension.gql('WHERE extID = :1', extID).get()
			if ext:
				if ext.developer == user or users.is_current_user_admin():
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
			if ext and ext.developer == user or users.is_current_user_admin():
				if self.request.get('title'):
					ext.title = self.request.get('title')
				else:
					ext.title = DEFAULT_EXTENSION_TITLE
				
				if self.request.get('type'):
					ext.type = self.request.get('type')
				else: # default to gadget if no type is sent
					ext.type = DEFAULT_EXTENSION_TYPE
				
				if ext.type == 'gadget':
					if self.request.get('gadgetURL'):
						url = self.request.get('gadgetURL')
						if not re.match('^https?:\/\/', url):
							url = 'http://' + url
						if not re.match('^https?:\/\/.+\..+', url):
							error = 'badurl'
						ext.gadgetURL = url
				else:
					ext.gadgetURL = None
				
				if ext.type == 'robot':
					if self.request.get('robotAddress'):
						address = self.request.get('robotAddress')
						if not re.match('.+@.+\..+', address):
							error = 'badaddress'
						else:
							ext.robotAddress = self.request.get('robotAddress')
				else:
					ext.robotAddress = None
				
				if self.request.get('description'):
					ext.description = self.request.get('description')
				else:
					ext.description = DEFAULT_EXTENSION_DESCRIPTION
				
				if self.request.get('category'):
					ext.category = self.request.get('category')
				else:
					ext.category = DEFAULT_EXTENSION_CATEGORY
				
				# If a new icon was uploaded,
				if self.request.get('icon'):
					# Get the icon <input>.
					iconFile = self.request.get('icon')
					# Make sure it is a PNG and return an error if it is not.
					icon = images.Image(image_data=iconFile)
					if icon.format != images.PNG:
						error = 'icontype'
					else:
						# Make sure it is the porper size.
						iconFile = images.resize(iconFile, 128, 128)
						# Overwrite the existing icon.
						ext.icon = db.Blob(iconFile)
				
				# Loop over the screenshot <input>s.
				screenshotFiles = self.request.get_all('screenshot')
				for i in range(len(screenshotFiles)):
					# Make sure something was actually uploaded in that <input>.
					if screenshotFiles[i]:
						# Make sure it is a PNG and return an error if it is not.
						screenshot = images.Image(image_data=screenshotFiles[i])
						if screenshot.format != images.PNG:
							error = 'screenshottype'
						else:
							# Make sure it is the proper size.
							screenshotFiles[i] = images.resize(screenshotFiles[i], 640, 400)
							# Put it in the extension's screenshots array.
							if i < len(ext.screenshots):
								ext.screenshots[i] = db.Blob(screenshotFiles[i])
							else:
								ext.screenshots.append(db.Blob(screenshotFiles[i]))
				
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

site = webapp.WSGIApplication([('/dev/new/?', NewExt),
                               ('/dev/edit/(\w{16})/?', EditExt),
                               ('/dev/?', DevDash),
                               ('/(.*)', OtherPage)],
                              debug=True)

def main():
	run_wsgi_app(site)

if __name__ == '__main__':
	main()
