#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.appengine.api import search
from google.appengine.ext import ndb

# The Python Markdown implementation by Waylan Limberg
import markdown
# The GitHub-Flavored Markdown
import gfm

from constants import *

class Extension(ndb.Model):
	extID = ndb.StringProperty() # The extension's unique ID 
	type = ndb.StringProperty() # “gadget” or “robot”
	developer = ndb.UserProperty()
	title = ndb.StringProperty()
	description = ndb.TextProperty()
	category = ndb.StringProperty()
	icon = ndb.BlobProperty()
	screenshots = ndb.BlobProperty(repeated=True)
	gadgetURL = ndb.StringProperty() # `None` for robots
	robotAddress = ndb.StringProperty() # `None` for gadgets
	
	def _pre_put_hook(self):
		# Fill in default values for fields.
		if self.title == None:
			self.title = DEFAULT_EXTENSION_TITLE
		if self.description == None:
			self.description = DEFAULT_EXTENSION_DESCRIPTION
		if self.type == None:
			self.type = DEFAULT_EXTENSION_TYPE
		if self.category == None:
			self.category = DEFAULT_EXTENSION_CATEGORY
	
	def _post_put_hook(self,future):
		# Update the extension's assosciated search document.
		doc = search.Document(
			doc_id=self.extID,
			fields=[
				search.TextField(name='title', value=self.title),
				search.HtmlField(name='description', value=self.htmlDescription),
				search.AtomField(name='developer', value=self.developer.nickname()),
				search.AtomField(name='type', value=self.type),
				search.AtomField(name='category', value=self.category),
				search.NumberField(name='rating', value=self.rating)
			]
		)
		search.Index(name=SEARCH_INDEX_NAME).put(doc)
	
	def getHTMLDescription(self):
		# Convert the Markdown in the description to HTML,
		# but escape any HTML added by the user.
		return markdown.markdown(text=gfm.gfm(self.description),safe_mode='escape')
	
	def getRatingCount(self):
		return Rating.gql('WHERE extID = :1 AND value != :2',self.extID,0).count(limit=None)
	
	def getRating(self):
		# Fetch the numbers of downvotes and upvotes and return the difference
		downvotes = Rating.gql('WHERE extID = :1 AND value = :2',self.extID,-1).count(limit=None)
		upvotes = Rating.gql('WHERE extID = :1 AND value = :2',self.extID,1).count(limit=None)
		return upvotes - downvotes
	
	def getUpvotePercentage(self):
		ratingCount = Rating.gql('WHERE extID = :1 AND value != :2',self.extID,0).count(limit=None)
		if ratingCount > 0: # prevent dividing by zero; the percents already default to zero
			return Rating.gql('WHERE extID = :1 AND value = :2',self.extID,1).count(limit=None) * 1.0 / ratingCount * 100
		else:
			return 0.0
	
	def getDownvotePercentage(self):
		ratingCount = Rating.gql('WHERE extID = :1 AND value != :2',self.extID,0).count(limit=None)
		if ratingCount > 0: # prevent dividing by zero; the percents already default to zero
			return Rating.gql('WHERE extID = :1 AND value = :2',self.extID,-1).count(limit=None) * 1.0 / ratingCount * 100
		else:
			return 0.0
	
	htmlDescription = property(getHTMLDescription)
	ratingCount = property(getRatingCount)
	rating = property(getRating)
	upvotePercentage = property(getUpvotePercentage)
	downvotePercentage = property(getDownvotePercentage)

class Rating(ndb.Model):
	value = ndb.IntegerProperty() # -1, 0, or 1
	extID = ndb.StringProperty() # The ID of the extension being voted on
	user = ndb.UserProperty() # The user who submitted this rating
	
	def _post_put_hook(self,future):
		ext = Extension.gql('WHERE extID = :1',self.extID).get()
		if ext:
			if ext.title == None:
				ext.title = DEFAULT_EXTENSION_TITLE
			if ext.description == None:
				ext.description = DEFAULT_EXTENSION_DESCRIPTION
			if ext.type == None:
				ext.type = DEFAULT_EXTENSION_TYPE
			if ext.category == None:
				ext.category = DEFAULT_EXTENSION_CATEGORY
			
			doc = search.Document(
				doc_id=ext.extID,
				fields=[
					search.TextField(name='title', value=ext.title),
					search.HtmlField(name='description', value=ext.htmlDescription),
					search.AtomField(name='type', value=ext.type),
					search.AtomField(name='category', value=ext.category),
					search.NumberField(name='rating', value=ext.rating)
				]
			)
			search.Index(name=SEARCH_INDEX_NAME).put(doc)

class User(ndb.Model):
	user = ndb.UserProperty()
	starred = ndb.StringProperty(repeated=True) # The list of starred extension IDs
