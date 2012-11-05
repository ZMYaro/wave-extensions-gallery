#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import os

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class DocPage(webapp.RequestHandler):
	def get(self,page):
		if not page or page == '':
			page = 'index'
		elif page == 'sidebar':
			page = '404'
		else:
			page = page[1:] # remove the initial slash
		
		docPath = 'templates/docs/' + page + '.html'
		
		if not os.path.exists(os.path.join(os.path.dirname(__file__), docPath)):
			docPath = 'templates/docs/404.html'
		
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {'title':'Documentation'}))
		path = os.path.join(os.path.dirname(__file__), 'templates/docs/sidebar.html')
		self.response.out.write(template.render(path, {}))
		path = os.path.join(os.path.dirname(__file__), docPath)
		self.response.out.write(template.render(path, {'baseURL':self.request.host_url}))
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class OtherPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {'title':'Error'}))
		path = os.path.join(os.path.dirname(__file__), 'templates/404.html')
		self.response.out.write(template.render(path, {}))
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))
		self.response.set_status(404);

site = webapp.WSGIApplication([('/docs(/.*)?', DocPage),
                               ('/.*', OtherPage)],
                              debug=True)

def main():
	run_wsgi_app(site)

if __name__ == '__main__':
	main()
