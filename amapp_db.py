from google.appengine.ext import db
from datetime import datetime, timedelta

class Art(db.Model):
	title=db.StringProperty(required=True)
	art=db.TextProperty()
	created=db.DateTimeProperty(auto_now_add=True)
	coords=db.GeoPtProperty()
	troll = db.StringProperty()
	
	def art_key(self):
		return self.key()
		
class Image(db.Model):
	image = db.BlobProperty(required = True)
	
	def img_key(self):
		return self.key()

class Documents(db.Model):
	title = db.StringProperty(required = True)
	doc = db.StringProperty()

class Blog_Entry(db.Model):
	subject = db.StringProperty(required=True)
	content = db.TextProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)
	tag = db.StringProperty(required=False)
	subtag = db.StringProperty(required = False)
	
	
	def ide(self):
		a = self.key()
		b = a.id()
		return b
		
	def rend(self,content):
		c = content.replace('\n','<br>')
		return c
		
	def rendhome(self,content):
		a = self.rend(content)
		b = a[:500]
		return b

class Blog_tags(db.Model):
	tag = db.StringProperty(required = True)

class Un_pw(db.Model):
	username = db.StringProperty(required=True)
	password = db.StringProperty(required=True)
	email_id = db.StringProperty()
	


class Blog_comments(db.Model):
	posted_by=db.StringProperty(required=True)
	comment=db.TextProperty(required=True)
	blog_id=db.StringProperty(required=True)
	posted_on=db.DateTimeProperty(auto_now_add=True)
	mail_id = db.StringProperty(required=False)
	
	def comment_hashed(self):
		table={}
		table["posted_by"]=self.posted_by
		table["posted_on"]=self.posted_on
		table["comment"]= self.rend(self.comment)
		return table
	
	def rend(self,content):
		c=content.replace('\n','<br>')
		return c
 
class Route(db.Model):
	source = db.StringProperty(required = True)
	dest = db.StringProperty(required = True)
	ts = db.DateTimeProperty(auto_now_add=True)
	toj = db.StringProperty(required = True)
	
	
	def getRoute(self, key):
		return db.get(key)
