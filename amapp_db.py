from google.appengine.ext import db


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
 
class user(db.Model):
	username = db.StringProperty(required=True)
	password = db.StringProperty(required=True)
	name = db.StringProperty(required=True)
	car = db.StringProperty()
	email_id = db.StringProperty()
	
class car_post(db.Model):
	username = db.StringProperty(required=True)
	post = db.TextProperty()
	posted_on=db.DateTimeProperty(auto_now_add=True)
	image = db.StringProperty()

class meetup(db.Model):
	venue = db.StringProperty(required=True)
	date = db.DateTimeProperty(required=True)
	organiser = db.StringProperty(required=True)
	info = db.TextProperty(required=True)
	
class Book(db.Model):
	isbn = db.StringProperty(required=True)
	name = db.StringProperty(required=True)
	author = db.StringProperty(required=True)
	qty = db.IntegerProperty(required =True)
	book_img = db.StringProperty()
	lang = db.StringProperty()
	description = db.TextProperty()
	rating = db.FloatProperty()
	pages = db.IntegerProperty()
	book_format = db.StringProperty()
	gr_link = db.StringProperty()
	def book_purchase_request(self, book_id):
		book = Book.get_by_id(int(book_id))
		if book and book.qty > 0:
			book.qty = book.qty -1
			book.put()
			return book
		else:
			return None
	def add_book(self, qty):
		self.qty = self.qty + int(qty)
		self.put()
	def id(self):
		a = self.key()
		b = a.id()
		return b
	
class order(db.Model):
	order_by = db.StringProperty(required=True)
	to = db.StringProperty(required=True)
	placed_time = db.DateTimeProperty(auto_now_add=True)
	approved_time = db.DateTimeProperty()
	shipped_time = db.DateTimeProperty()
	delivered_time = db.DateTimeProperty()
	cancel_time = db.DateTimeProperty()
	status = db.StringProperty(required=True)
	isbn = db.StringProperty(required=True)
	
