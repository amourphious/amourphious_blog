import webapp2
import cgi
import re
import os
import logging
import jinja2
import random
import string
import hashlib
import urllib2
import json


from xml.dom.minidom import Document
from xml.dom import minidom

from datetime import datetime, timedelta
from collections import namedtuple

from google.appengine.api import mail 
from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.api import users

class User(ndb.Model):
	name = ndb.StringProperty(required=True)
	email = ndb.StringPropperty(required=True)

class Comment(ndb.Model):
	comment = ndb.TextProperty(required=True)
	postedBy = ndb.StructuredProperty(User, required=True)
	time = ndb.DateTimeProperty(required=True, auto_now_add=True)

class Post(ndb.Model):
	title = ndb.StringProperty(reuqitred=True)
	post = ndb.TextProperty(required=True)
	commnets = ndb.StructuredProperty(Comment, repeated=True)
	time = ndb.DateTimeProperty(required=True, auto_now_add=True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a,**kw)
		
	def render_str(self,template,**params):
		t=jinja_env.get_template(template)
		return t.render(params)
		
	def render(self,template,**kw):
		self.write(self.render_str(template,**kw))

class BlogPermalink(Handler):
	def get(self):
		posts = Post.query()
		for post in posts:
			self.write("""<h2>%s
			</h2><p>%s</p><h3>Comments</h3>""")
			for comment in list(post.comments):
				self.write("""<p>%s<p><h6>%s</h6><h6>%s</h6>""")

