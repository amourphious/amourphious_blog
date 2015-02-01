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
 
from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import users


template_dir=os.path.join(os.path.dirname(__file__),'templates')
jinja_env=jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),autoescape = True)

def hash_str(s):
	return hashlib.sha256(s).hexdigest()
	


def make_salt():
	return ''.join(random.choice(string.letters) for x in xrange(5))
	


def make_pw_hash(name,pw,salt=None):
	if not salt:
		salt=make_salt()
	h=hashlib.sha256(name+pw+salt).hexdigest()
	return "%s|%s" %(h,salt)
	

    
def valid_pw(name,pw,h):
	salt=h.split('|')[1]
	return make_pw_hash(name,pw,salt)

def valid_login(name,pw,h):
	salt=h.split('|')[1]
	return (make_pw_hash(name,pw,salt) == h)
		
		
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE=re.compile(r"^.{3,20}$")
MAIL_RE=re.compile(r"^[\S]+@[\S]+\.[\S]+$")



def escape_html(s):
	cgi.escape(s,quote=True)
	return s



def valid_username(username):
	return USER_RE.match(username)



def valid_password(password):
	return PASS_RE.match(password)
	


def valid_email(mail):
	return MAIL_RE.match(mail)


			
table_re=re.compile(r"<table.*?>")
row_re=re.compile(r"<tr.*?>")
column_re=re.compile(r"<td.*?>")
tag_re=re.compile(r"<.*?>")
ecs_re=re.compile(r"&.*?;")

def split_htm(dre,content,endtag):
	lst=re.split(dre,content)
	dst=[]
	for l in lst:
		dst.append(l.replace(endtag,''))
	return dst



class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a,**kw)
		
	def render_str(self,template,**params):
		t=jinja_env.get_template(template)
		return t.render(params)
		
	def render(self,template,**kw):
		self.write(self.render_str(template,**kw))
