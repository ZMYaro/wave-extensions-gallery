#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class MainPage(webapp.RequestHandler):
	def get(self, page):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {'stylesheet':'landing'}))
		path = os.path.join(os.path.dirname(__file__), 'templates/landing.html')
		self.response.out.write(template.render(path, {}))
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class AboutPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {'title':'About'}))
		path = os.path.join(os.path.dirname(__file__), 'templates/about.html')
		self.response.out.write(template.render(path, {}))
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class RobotsTxt(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write('User-agent: *\nDisallow: /')

class FaviconHandler(webapp.RequestHandler):
	def get(self):
		self.response.set_status(301)
		self.redirect('/static/images/gadget_icon_16x16.ico')

class GooglePlusRedirect(webapp.RequestHandler):
	def get(self):
		self.response.set_status(301)
		self.redirect('http://plus.google.com/111054500428067493902')

class OtherPage(webapp.RequestHandler):
	def get(self, page):
		if page[:6] == 'robots':
			self.redirect('/gallery/robots' + page[6:])
		elif page[:7] == 'gadgets':
			self.redirect('/gallery/gadgets' + page[7:])
		else:
			path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
			self.response.out.write(template.render(path, {'title':'Error'}))
			path = os.path.join(os.path.dirname(__file__), 'templates/404.html')
			self.response.out.write(template.render(path, {}))
			path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
			self.response.out.write(template.render(path, {}))
			self.response.set_status(404);

site = webapp.WSGIApplication([('/(index\.html)?', MainPage),
                               ('/about', AboutPage),
                               ('/robots.txt', RobotsTxt),
                               ('/favicon.ico', FaviconHandler),
                               ('/\+/?', GooglePlusRedirect),
                               ('/(.*)', OtherPage)],
                              debug=True)

def main():
	run_wsgi_app(site)

if __name__ == '__main__':
	main()
