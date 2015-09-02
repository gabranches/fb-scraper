import time
# SQLAlchemy imports
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Post(Base):
	__tablename__ = 'posts'
	post_full_id = Column(String, primary_key=True)
	post_id = Column(Integer)
	fb_org_id = Column(Integer)
	created_time = Column(String)
	message = Column(String)
	type = Column(String)
	shares = Column(Integer)
	like_count = Column(Integer)
	comments_count = Column(Integer)
	org_name = Column(String)
	link = Column(String)
	url = Column(String)
	status_type = Column(String)
	hashtags = Column(String)
	hashtags_count = Column(Integer)
	date_collected = Column(String)
	mentions = Column(String)
	mentions_count = Column(Integer)
	comment_order = Column(String)

	def __init__(self, data):
		self.post_full_id = data['id'] if 'id' in data else None
		self.post_id = int(data['id'].split('_')[0]) if 'id' in data else None
		self.fb_org_id = int(data['id'].split('_')[1]) if 'id' in data else None
		self.created_time = data['created_time'] if 'created_time' in data else None
		self.message = data['message'] if 'message' in data else None
		self.shares = data['shares']['count'] if 'shares' in data else 0
		self.like_count = data['likes']['summary']['total_count'] if 'likes' in data else 0
		self.comments_count = data['comments_count'] if 'comments_count' in data else 0
		self.type = data['type'] if 'type' in data else None
		self.org_name = data['org_name'] if 'org_name' in data else None
		self.link = data['link'] if 'link' in data else None
		self.url = data['url'] if 'url' in data else None
		self.status_type = data['status_type'] if 'status_type' in data else None
		self.hashtags = data['hashtags'] if 'hashtags' in data else None
		self.hashtags_count = data['hashtags_count'] if 'hashtags_count' in data else 0
		self.date_collected = time.strftime("%Y-%m-%d")
		self.mentions = data['mentions'] if 'mentions' in data else None
		self.mentions_count = data['mentions_count'] if 'mentions_count' in data else 0
		self.comment_order =  data['comment_order'] if 'comment_order' in data else None


class Comment(Base):
	__tablename__ = 'comments'
	comment_id = Column(String, primary_key=True)
	parent_post_full_id = Column(String)
	message = Column(String)
	like_count = Column(Integer)
	created_time = Column(String)
	hashtags = Column(String)
	hashtags_count = Column(String)
	commenter_id = Column(Integer)
	mentions = Column(String)
	mentions_count = Column(Integer)

	def __init__(self, data, parent_post):
		self.comment_id = data['id'] if 'id' in data else None
		self.parent_post_full_id = parent_post
		self.message = data['message'] if 'message' in data else None
		self.like_count = int(data['like_count']) if 'like_count' in data else 0
		self.created_time = data['created_time'] if 'created_time' in data else None
		self.hashtags = data['hashtags'] if 'hashtags' in data else None
		self.hashtags_count = data['hashtags_count'] if 'hashtags_count' in data else 0
		self.commenter_id = data['from']['id'] if 'from' in data else None
		self.mentions = data['mentions'] if 'mentions' in data else None
		self.mentions_count = data['mentions_count'] if 'mentions_count' in data else 0
