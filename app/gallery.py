#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import os

from google.appengine.api import search
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

# The Python Markdown implementation by Waylan Limberg
import markdown
# The GitHub-Flavored Markdown
import gfm

from datastore import Extension,Rating,User

def searchFor(query):
	# Search for the query
	results = search.Index(name='galleryindex').search(query)
	# Create a list for the returned extensions
	extlist = []
	# Loop over the scored documents
	for result in results.results:
		# Do a datastore lookup for each extension ID
		ext = Extension.gql('WHERE extID = :1', result._doc_id).get()
		# If the  extension is found, fetch its rating info. and add it to the list
		if ext:
			extlist.append(ext)
	
	return extlist

class MainPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {'stylesheet':'gallery'}))
		
		extlist = Extension.gql('').fetch(limit=None)
		
		path = os.path.join(os.path.dirname(__file__), 'templates/gallerylist.html')
		self.response.out.write(template.render(path, {'extlist':extlist}))
		
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class GadgetsPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {'stylesheet':'gallery'}))
		
		extlist = Extension.gql('WHERE type = :1','gadget').fetch(limit=None)
		
		path = os.path.join(os.path.dirname(__file__), 'templates/gallerylist.html')
		self.response.out.write(template.render(path, {'extlist':extlist}))
		
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class RobotsPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {'stylesheet':'gallery'}))
		
		extlist = Extension.gql('WHERE type = :1','robot').fetch(limit=None)
		
		path = os.path.join(os.path.dirname(__file__), 'templates/gallerylist.html')
		self.response.out.write(template.render(path, {'extlist':extlist}))
		
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class CategoryPage(webapp.RequestHandler):
	def get(self, category):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {'stylesheet':'gallery'}))
		
		# Search for extensions in the category
		extlist = Extension.gql('WHERE category = :1',category).fetch(limit=None)
		#results = search.Index(name='galleryindex').search('category:' + category)
		
		# Create a list for the returned extensions
		#extlist = []
		# Loop over the scored documents
		#for result in results.results:
			# Do a datastore lookup for each extension ID
		#	ext = Extension.gql('WHERE extID = :1', result._doc_id).get()
			# If the  extension is found, and add it to the list
		
		category = category[0].upper() + category[1:].lower()
		
		path = os.path.join(os.path.dirname(__file__), 'templates/gallerylist.html')
		self.response.out.write(template.render(path, {'query':category,'extlist':extlist}))
		
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class SearchHandler(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {'stylesheet':'gallery'}))
		
		# Get the query
		query = self.request.get('q')
		extlist = searchFor(query)
		
		query = u'Results for \u201c' + query + u'\u201d'
		
		path = os.path.join(os.path.dirname(__file__), 'templates/gallerylist.html')
		self.response.out.write(template.render(path, {'query':query,'extlist':extlist}))
		
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
			# Convert the Markdown in the description to HTML,
			# but escape any HTML added by the user.
			ext.description = markdown.markdown(text=gfm.gfm(ext.description), safe_mode='escape')
			
			# Add the Extension to the template vars dictionary and
			# set other template vars to their default values.
			templateVars = {
				'ext':ext,
				'userRating':None,
				'starred':False,
				'userIsDev':False
			}
			
			if ext.developer:
				templateVars['devname'] = ext.developer.nickname()
			
			user = users.get_current_user()
			if user:
				userEntry = User.gql('WHERE user = :1',user).get()
				if userEntry:
					if extID in userEntry.starred:
						templateVars['starred'] = True
				userRating = Rating.gql('WHERE user = :1 AND extID = :2',user,extID).get()
				if userRating:
					templateVars['userRating'] = userRating.value
				else:
					templateVars['userRating'] = 0 # Every user's default vote is zero
				
				if user == ext.developer:
					templateVars['userIsDev'] = True
			
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
				rating = Rating.gql('WHERE user = :1 AND extID = :2',user,extID).get()
				if not rating:
					rating = Rating()
					rating.user = user
					rating.extID = extID
				if value == 'up':
					rating.value = 1
				elif value == 'down':
					rating.value = -1
				else:
					rating.value = 0
				rating.put()
				self.redirect('/gallery/info/' + extID)

class IndexUpdater(webapp.RequestHandler):
	def get(self):
		if not users.get_current_user():
			self.redirect(users.create_login_url(self.request.uri))
			return
		elif not users.is_current_user_admin():
			self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
			self.response.out.write('Error 401')
			self.response.set_status(401)
			return
		
		self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
		
		self.response.out.write('Loading extensions from the datastore...\n\n')
		
		extlist = Extension.gql('').fetch(limit=None)
		
		galleryIndex = search.Index(name='galleryindex')
		for ext in extlist:
			doc = search.Document(
				doc_id=ext.extID,
				fields=[
					search.TextField(name='title', value=ext.title),
					search.TextField(name='description', value=ext.description),
					search.AtomField(name='developer', value=ext.developer.nickname()),
					search.AtomField(name='type', value=ext.type),
					search.AtomField(name='category', value=ext.category),
					search.NumberField(name='rating', value=ext.rating)
				]
			)
			galleryIndex.put(doc)
			self.response.out.write(u'Updated search Document for \u201c' + ext.title + u'\u201d (' + ext.extID + ')\n')
		
		self.response.out.write('\nThe search index has been updated.')
		

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
                               ('/gallery/category/(\w+)', CategoryPage),
                               ('/gallery/search', SearchHandler),
                               ('/gallery/info/(\w{16})/?', InfoPage),
                               ('/gallery/icon/(\w{16})\.png', IconFetcher),
                               ('/gallery/(up|down|null)vote/(\w{16})/?', RatingHandler),
                               ('/gallery/updateindex', IndexUpdater),
                               ('/(.*)', OtherPage)],
                              debug=True)

def main():
	run_wsgi_app(site)

if __name__ == '__main__':
	main()
