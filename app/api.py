#!/usr/bin/python
# -*- coding: utf-8 -*-

import cgi
import json
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
		upvotePercent = 0.0
		downvotePercent = 0.0
	return ratingCount,upvotePercent,downvotePercent

def extToDict(ext,baseURL=''):
	ext = {
		'id': ext.extID,
		'type': ext.type,
		'developer': ({
			'email':ext.developer.email(),
			'nickname':ext.developer.nickname()
			#'user_id':ext.developer.user_id()
		} if ext.developer != None else {      # Do not attempt to get
			'email': None,                     # developer properties
			'nickname': None                   # if developer is None.
		}),
		'title': ext.title,
		'description': ext.description,
		'iconURL': baseURL + '/gallery/icon/' + ext.extID + '.png',
		'gadgetURL': ext.gadgetURL,
		'robotAddress': ext.robotAddress
	}
	return ext

class ListHandler(webapp.RequestHandler):
	def get(self,format):
		if format == 'json':
			# set the type to JSON
			self.response.headers['Content-Type'] = 'application/json'
			
			if self.request.get('type'):
				#if self.request.get('type') not in ['gadget','robot']:
					# prevent illegal extension types (may want to make this list global)
				#	self.response.out.write('{\"error\":\"Parameter \\\"type\\\" must be \\\"gadget\\\" or \\\"robot\\\"\"}')
				#	self.response.set_status(404)
				#	return
				extList = Extension.gql('WHERE type = :1',self.request.get('type')).fetch(limit=None)
			else:
				extList = Extension.gql('').fetch(limit=None)
			
			extDictList = []
			for i in range(len(extList)):
				# Skip extensions without IDs (this case should never happen)
				if extList[i].extID == None:
					continue
				# Change the extension to a dictionary, which can then be converted to JSON
				extList[i] = extToDict(extList[i],self.request.host_url)
				# Add rating information to each Extension object
				extList[i]['ratingCount'],extList[i]['upvotePercent'],extList[i]['downvotePercent'] = getRatingInfo(extList[i]['id'])
				# Add the dictionary to the dictionary list
				# (I used a separate list here to avoid confusions that could
				# occur when removing invalid items from the original list.)
				extDictList.append(extList[i])
			
			# Convert the dictionaries to JSON
			self.response.out.write(json.dumps(extDictList))
		else:
			self.response.headers['Content-Type'] = 'text/plain'
			self.response.out.write('Error 404')
			self.response.set_status(404)

class ExtInfo(webapp.RequestHandler):
	def get(self,format):
		if format == 'json':
			# set the type to JSON
			self.response.headers['Content-Type'] = 'application/json'
			
			extID = self.request.get('id')
			if not extID:
				self.response.out.write('{\"error\":\"Required parameter \\\"id\\\" was missing\"}')
				self.response.set_status(404)
				return
			
			ext = Extension.gql('WHERE extID = :1',extID).get()
			
			if not ext:
				self.response.out.write('{\"error\":\"No extension found with ID \\\"' + extID + '\\\"\"}')
				self.response.set_status(404)
				return
			
			# change the extension to a dictionary, which can then be converted to JSON
			ext = extToDict(ext,self.request.host_url)
			# add rating information to each Extension object
			ext['ratingCount'],ext['upvotePercent'],ext['downvotePercent'] = getRatingInfo(ext['id'])
			
			# convert the dictionary to JSON
			self.response.out.write(json.dumps(ext))
		else:
			self.response.headers['Content-Type'] = 'text/plain'
			self.response.out.write('Error 404')
			self.response.set_status(404)

class OtherPage(webapp.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.out.write('Error 404')
		self.response.set_status(404)

site = webapp.WSGIApplication([('/api/v0/list.(\w+)', ListHandler),
                               ('/api/v0/info.(\w+)', ExtInfo),
                               #('/api/v1/search.(\w+)', SearchHandler),
                               ('/.*', OtherPage)],
                              debug=True)

def main():
	run_wsgi_app(site)

if __name__ == '__main__':
	main()
