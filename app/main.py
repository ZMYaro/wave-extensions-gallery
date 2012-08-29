#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import os

from google.appengine.dist import use_library
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

use_library('django', '1.2')

class MainPage(webapp.RequestHandler):
	def get(self, page):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {}))
		path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
		self.response.out.write(template.render(path, {}))
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class AboutPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {'title':'About','stylesheet':'about'}))
		path = os.path.join(os.path.dirname(__file__), 'templates/about.html')
		self.response.out.write(template.render(path, {}))
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

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
                               ('/(.*)', OtherPage)],
                              debug=True)

def main():
	run_wsgi_app(site)

if __name__ == '__main__':
	main()
