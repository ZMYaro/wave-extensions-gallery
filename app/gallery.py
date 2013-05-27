#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import os

from google.appengine.api import search
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from constants import *
from datastore import Extension,Rating,User
from util import parseInt

def searchFor(query='',limit=DEFAULT_QUERY_LIMIT,offset=DEFAULT_QUERY_OFFSET,sortBy=SORT_BEST_MATCH):
	# Create a sort expression for the given sort method, if any.
	expressions = None
	if sortBy == SORT_TOP_RATING:
		expressions = [
			search.SortExpression(
				expression='rating',
				direction=search.SortExpression.DESCENDING,
				default_value=0
			)
		]
		
	
	# Create the search query.
	searchQuery = search.Query(
		query_string=query,
		options=search.QueryOptions(
			limit=limit,
			offset=offset,
			sort_options=search.SortOptions(
				# Find best matches unless a different sort method is chosen.
				match_scorer=(search.MatchScorer() if sortBy == SORT_BEST_MATCH else None),
				expressions=expressions,
				limit=limit
			)
		)
	)
	
	# Search for the query
	results = search.Index(name=SEARCH_INDEX_NAME).search(searchQuery)
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
		
		#extlist = Extension.gql('').fetch(limit=None)
		extlist = searchFor('',limit=20,sortBy=SORT_TOP_RATING)
		
		path = os.path.join(os.path.dirname(__file__), 'templates/gallerylist.html')
		self.response.out.write(template.render(path, {'query':'Top Extensions','extlist':extlist}))
		
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class GadgetsPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {'stylesheet':'gallery'}))
		
		#extlist = Extension.gql('WHERE type = :1','gadget').fetch(limit=None)
		extlist = searchFor('type:gadget',limit=20,sortBy=SORT_TOP_RATING)
		
		path = os.path.join(os.path.dirname(__file__), 'templates/gallerylist.html')
		self.response.out.write(template.render(path, {'query':'Top Gadgets','extlist':extlist}))
		
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class RobotsPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {'stylesheet':'gallery'}))
		
		#extlist = Extension.gql('WHERE type = :1','robot').fetch(limit=None)
		extlist = searchFor('type:robot',limit=20,sortBy=SORT_TOP_RATING)
		
		path = os.path.join(os.path.dirname(__file__), 'templates/gallerylist.html')
		self.response.out.write(template.render(path, {'query':'Top Robots','extlist':extlist}))
		
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class CategoryPage(webapp.RequestHandler):
	def get(self, category):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {'stylesheet':'gallery'}))
		
		# Get the list of extensions in the category, sorted by rating
		#extlist = Extension.gql('WHERE category = :1',category).fetch(limit=None)
		extlist = searchFor('category:' + category,limit=20,sortBy=SORT_TOP_RATING)
		
		category = 'Top ' +\
			category[0].upper() + category[1:].lower() +\
			' Extensions'
		
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

class IconHandler(webapp.RequestHandler):
	def get(self,extID):
		ext = Extension.gql('WHERE extID = :1',extID).get()
		if ext:
			if ext.icon:
				self.response.headers['Content-Type'] = 'image/png'
				self.response.out.write(ext.icon)
			else:
				self.redirect('/static/images/gadget_icon_128x128.png')
		else:
			self.error(404)

class ScreenshotHandler(webapp.RequestHandler):
	def get(self,extID,number):
		ext = Extension.gql('WHERE extID = :1',extID).get()
		number = parseInt(number,-1)
		if number != -1 and ext and ext.screenshots and number < len(ext.screenshots):
			self.response.headers['Content-Type'] = 'image/png'
			self.response.out.write(ext.screenshots[number])
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
		
		galleryIndex = search.Index(name=SEARCH_INDEX_NAME)
		for ext in extlist:
			if ext.title == None:
				ext.title = ''
			if ext.description == None:
				ext.description = ''
			if ext.type == None:
				ext.type = 'gadget'
			if ext.category == None:
				ext.category = 'other'
			
			doc = search.Document(
				doc_id=ext.extID,
				fields=[
					search.TextField(name='title', value=ext.title),
					search.HtmlField(name='description', value=ext.htmlDescription),
					search.AtomField(name='developer', value=ext.developer.nickname() if ext.developer else ''),
					search.AtomField(name='type', value=ext.type),
					search.AtomField(name='category', value=ext.category),
					search.NumberField(name='rating', value=ext.rating)
				]
			)
			galleryIndex.put(doc)
			self.response.out.write('Updated search Document for \"' + ext.title + '\" (' + ext.extID + ')\n')
		
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
                               ('/gallery/icon/(\w{16})\.png', IconHandler),
                               ('/gallery/screenshot/(\w{16})_([0-9])\.png', ScreenshotHandler),
                               ('/gallery/(up|down|null)vote/(\w{16})/?', RatingHandler),
                               ('/gallery/updateindex', IndexUpdater),
                               ('/(.*)', OtherPage)],
                              debug=True)

def main():
	run_wsgi_app(site)

if __name__ == '__main__':
	main()
