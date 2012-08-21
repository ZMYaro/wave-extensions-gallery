import cgi
import os

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class MainPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {}))
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class GadgetsPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {}))
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class RobotsPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {}))
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class InfoPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {}))
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class OtherPage(webapp.RequestHandler):
	def get(self, page):
		if page == 'extension':
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
                               ('/gallery/info/(.*)', InfoPage),
                               ('/(.*)', OtherPage)],
                              debug=True)

def main():
	run_wsgi_app(site)

if __name__ == '__main__':
	main()
