# SQLAlchemy imports
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Post(Base):
	__tablename__ = 'posts'

	post_id = Column(String, primary_key=True)
	created_time = Column(String)
	message = Column(String)
	type = Column(String)
	shares = Column(Integer)
	like_count = Column(Integer)
	comments_count = Column(Integer)

	def __init__(self, data):
		self.post_id = data['id'] if 'id' in data else None
		self.created_time = data['created_time'] if 'created_time' in data else None
		self.message = data['message'] if 'message' in data else None
		self.shares = data['shares']['count'] if 'shares' in data else 0
		self.like_count = data['likes']['summary']['total_count'] if 'likes' in data else 0
		self.comments_count = data['comments_count'] if 'comments_count' in data else 0
		self.type = data['type'] if 'type' in data else None

class Comment(Base):
	__tablename__ = 'comments'

	comment_id = Column(String, primary_key=True)
	post_id = Column(Integer)
	message = Column(String)
	like_count = Column(Integer)

	def __init__(self, data, parent_post):
		self.comment_id = data['id'] if 'id' in data else None
		self.post_id = parent_post
		self.message = data['message'] if 'message' in data else None
		self.like_count = int(data['like_count']) if 'like_count' in data else 0
