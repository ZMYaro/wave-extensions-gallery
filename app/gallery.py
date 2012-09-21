#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from datastore import Extension,Rating,User

def getRatingInfo(extID):
	ratingCount = Rating.gql('WHERE extID = :1 AND value != :2',extID,0).count(limit=None)
	if ratingCount > 0: # prevent dividing by zero; the percents already default to zero
		upvotePercent = Rating.gql('WHERE extID = :1 AND value = :2',extID,1).count(limit=None) * 1.0 / ratingCount * 100
		downvotePercent = 100 - upvotePercent
	else:
		upvotePercent = 0
		downvotePercent = 0
	return ratingCount,upvotePercent,downvotePercent

class MainPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {'stylesheet':'gallery'}))
		
		extlist = Extension.gql('').fetch(limit=None)
		
		for ext in extlist:
			ext.ratingCount,ext.upvotePercent,ext.downvotePercent = getRatingInfo(ext.extID)
		
		path = os.path.join(os.path.dirname(__file__), 'templates/gallerylist.html')
		self.response.out.write(template.render(path, {'extlist':extlist}))
		
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class GadgetsPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {}))
		
		#extlist = Extension.gql('WHERE type = :1', 'gadget').fetch(None)
		self.response.out.write('[Featured Gadgets]')
		
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class RobotsPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {}))
		self.response.out.write('[Featured Robots]')
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class InfoPage(webapp.RequestHandler):
	def get(self,extID):
		ext = Extension.gql('WHERE extID = :1',extID).get()
		
		if not ext:
			path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
			self.response.out.write(template.render(path, {'title':'Extension Not Found'}))
			path = os.path.join(os.path.dirname(__file__), 'templates/ext404.html')
			self.response.out.write(template.render(path, {}))
			self.response.set_status(404);
		else:
			templateVars = {
				'ext':ext,
				'devname':ext.developer.nickname(),
				'upvotePercent':0,
				'downvotePercent':0,
				'ratingCount':0,
				'userRating':0,
				'starred':False
			}
			
			templateVars['ratingCount'],templateVars['upvotePercent'],templateVars['downvotePercent'] = getRatingInfo(extID)
			
			user = users.get_current_user()
			if user:
				userEntry = User.gql('WHERE user = :1',user).get()
				if userEntry:
					if extID in userEntry.starred:
						templateVars['starred'] = True
				userRating = Rating.gql('WHERE user = :1 AND extID = :2',user,extID).get()
				if userRating:
					templateVars['userRating'] = userRating.value
			
			path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
			self.response.out.write(template.render(path, {'title':ext.title,'stylesheet':'gallery'}))
			path = os.path.join(os.path.dirname(__file__), 'templates/info.html')
			self.response.out.write(template.render(path, templateVars))
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class IconFetcher(webapp.RequestHandler):
	def get(self,extID):
		ext = Extension.gql('WHERE extID = :1',extID).get()
		if ext.icon:
			self.response.headers['Content-Type'] = 'image/png'
			self.response.out.write(ext.icon)
		else:
			self.error(404)

class RatingHandler(webapp.RequestHandler):
	def get(self,value,extID):
		user = users.get_current_user()
		if not user:
			self.redirect(users.create_login_url(self.request.uri))
		else:
			if Extension.gql('WHERE extID = :1',extID).count(limit=1) == 0:
				self.error(404)
			else:
				rating = Rating.gql('WHERE voter = :1 AND extID = :2',user,extID).get()
				if not rating:
					rating = Rating()
					rating.voter = user
					rating.extID = extID
				if value == 'up':
					rating.value = 1
				elif value == 'down':
					rating.value = -1
				else:
					rating.value = 0
				rating.put()
				self.redirect('/gallery/info/' + extID)

class OtherPage(webapp.RequestHandler):
	def get(self,page):
		if page == 'info':
			self.redirect('/gallery')
		else:
			path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
			self.response.out.write(template.render(path, {}))
			path = os.path.join(os.path.dirname(__file__), 'templates/404.html')
			self.response.out.write(template.render(path, {}))
			path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
			self.response.out.write(template.render(path, {}))
			self.response.set_status(404);

site = webapp.WSGIApplication([('/gallery', MainPage),
                               ('/gallery/gadgets', GadgetsPage),
                               ('/gallery/robots', RobotsPage),
                               ('/gallery/info/(\w{16})/?', InfoPage),
                               ('/gallery/icon/(\w{16})\.png', IconFetcher),
                               ('/gallery/(up|down|null)vote/(\w{16})/?', RatingHandler),
                               ('/(.*)', OtherPage)],
                              debug=True)

def main():
	run_wsgi_app(site)

if __name__ == '__main__':
	main()
