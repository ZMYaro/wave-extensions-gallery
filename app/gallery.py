#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import os

from google.appengine.api import search
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from datastore import Extension,Rating,User

galleryIndex = search.Index(name='galleryindex')

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
		self.response.out.write(template.render(path, {'stylesheet':'gallery'}))
		
		extlist = Extension.gql('WHERE type = :1','gadget').fetch(limit=None)
		for ext in extlist:
			ext.ratingCount,ext.upvotePercent,ext.downvotePercent = getRatingInfo(ext.extID)
		path = os.path.join(os.path.dirname(__file__), 'templates/gallerylist.html')
		self.response.out.write(template.render(path, {'extlist':extlist}))
		
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class RobotsPage(webapp.RequestHandler):
	def get(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {'stylesheet':'gallery'}))
		
		extlist = Extension.gql('WHERE type = :1','robot').fetch(limit=None)
		for ext in extlist:
			ext.ratingCount,ext.upvotePercent,ext.downvotePercent = getRatingInfo(ext.extID)
		path = os.path.join(os.path.dirname(__file__), 'templates/gallerylist.html')
		self.response.out.write(template.render(path, {'extlist':extlist}))
		
		path = os.path.join(os.path.dirname(__file__), 'templates/foot.html')
		self.response.out.write(template.render(path, {}))

class CategoryPage(webapp.RequestHandler):
	def get(self, category):
		path = os.path.join(os.path.dirname(__file__), 'templates/head.html')
		self.response.out.write(template.render(path, {'stylesheet':'gallery'}))
		
		# Search for extensions in the category
		results = galleryIndex.search('category:' + category)
		
		# Create a list for the returned extensions
		extlist = []
		# Loop over the scored documents
		for result in results.results:
			# Do a datastore lookup for each extension ID
			ext = Extension.gql('WHERE extID = :1', result._doc_id).get()
			# If the  extension is found, fetch its rating info. and add it to the list
			if ext:
				ext.ratingCount,ext.upvotePercent,ext.downvotePercent = getRatingInfo(ext.extID)
				extlist.append(ext)
		
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
		# Search for the query
		results = galleryIndex.search(query)
		# Create a list for the returned extensions
		extlist = []
		# Loop over the scored documents
		for result in results.results:
			# Do a datastore lookup for each extension ID
			ext = Extension.gql('WHERE extID = :1', result._doc_id).get()
			# If the  extension is found, fetch its rating info. and add it to the list
			if ext:
				ext.ratingCount,ext.upvotePercent,ext.downvotePercent = getRatingInfo(ext.extID)
				extlist.append(ext)
		
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
			templateVars = {
				'ext':ext,
				'upvotePercent':0,
				'downvotePercent':0,
				'ratingCount':0,
				'userRating':0,
				'starred':False
			}
			
			if ext.developer:
				templateVars['devname'] = ext.developer.nickname()
			
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

class IndexRebuilder(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			self.response.headers['Content-Type'] = 'text/plain'
			if users.is_current_user_admin():
				# Clear the existing index
				while True:
					# Get a list of documents populating only the doc_id field and extract the ids.
					docIDs = [doc.doc_id for doc in galleryIndex.list_documents(ids_only=True)]
					if not docIDs:
						break
					# Remove the documents for the given ids from the Index.
					galleryIndex.remove(docIDs)
				
				extlist = Extension.gql('').fetch(limit=None)
				ratinglist = Rating.gql('').fetch(limit=None)
				for ext in extlist:
					rating = getRatingInfo(ext.extID)[1]
					doc = search.Document(
						doc_id=ext.extID,
						fields=[
							search.TextField(name='title', value=ext.title),
							search.TextField(name='description', value=ext.description),
							search.AtomField(name='type', value=ext.type),
							search.AtomField(name='category', value=ext.category),
							search.NumberField(name='rating', value=rating)
						]
					)
					self.response.out.write('Created document for ' + ext.title + ' (' + ext.extID + ')\n')
					try:
						galleryIndex.add(doc)
						self.response.out.write('Successfully added document to index\n')
					except search.Error:
						self.response.out.write('Failed to add document to index\n')
				self.response.out.write('Done!')
			else:
				self.response.out.write('Access denied')
				self.response.set_status(401)
		else:
			self.redirect(users.create_login_url(self.request.uri))

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

class RatingMigrator(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		ratings = Rating.gql('').fetch(limit=None)
		for rating in ratings:
			if rating.user == None and rating.voter != None:
				rating.user = rating.voter
				rating.voter = None
				rating.put()
				self.response.out.write('Migrated ' + rating.user.email() + '\'s rating of extension ' + rating.extID + '\n')
		self.response.out.write('Done migrating ratings.')
		

site = webapp.WSGIApplication([('/gallery', MainPage),
                               ('/gallery/gadgets', GadgetsPage),
                               ('/gallery/robots', RobotsPage),
                               ('/gallery/category/(\w+)', CategoryPage),
                               ('/gallery/search', SearchHandler),
                               ('/gallery/info/(\w{16})/?', InfoPage),
                               ('/gallery/icon/(\w{16})\.png', IconFetcher),
                               ('/gallery/(up|down|null)vote/(\w{16})/?', RatingHandler),
                               ('/gallery/rebuildindex', IndexRebuilder),
                               ('/gallery/migrateratings', RatingMigrator),
                               ('/(.*)', OtherPage)],
                              debug=True)

def main():
	run_wsgi_app(site)

if __name__ == '__main__':
	main()
