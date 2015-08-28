import json
import urllib2
import time
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
from db_setup import Post, Comment


class Scrape:
	def __init__(self):
		engine = create_engine('sqlite:///fb-scraper.db', echo=False)
		Session = sessionmaker(bind=engine)
		self.session = Session()

	def fetch_app_access_token(self, fb_app_id, fb_app_secret):
		'''Get Facebook acess token'''
		resp = urllib2.urlopen(
			'https://graph.facebook.com/oauth/access_token?client_id=' +
			fb_app_id + '&client_secret=' + fb_app_secret +
			'&grant_type=client_credentials')

		if resp.getcode() == 200:
			return resp.read().split("=")[1]
		else:
			return None

	def get_page(self, page_name, num_pages, fields, limit, sleep_time):
		'''Get Facebook page info'''
		access_token = self.fetch_app_access_token('1018392914858570', '72cf8c8a02b6e9315a11d7f0d714841d')
		url = 'https://graph.facebook.com/{0}/feed?access_token={1}&fields={2}&limit={3}'.format(page_name, access_token, ','.join(fields), limit)
		print url
		for page in xrange(0, num_pages):
			print url
			print '\nGETTING PAGE {} DATA...'.format(page+1)		

			data = None
			while data is None:
				try:
					data = json.load(urllib2.urlopen(url))
				except KeyboardInterrupt:
					raise
				except urllib2.URLError:
					print "500 ERROR. TRYING AGAIN."
					pass
				except:
					print "ERROR. TRYING AGAIN."
					pass

				

			for post in data['data']:
				# Only get Post data if it doesn't already exist in db
				if self.session.query(exists().where(Post.post_id==post['id'])).scalar() == 0:

					# Get comments
					if 'comments' in post.keys():
						post['comments_count'] = self.get_comments(post['comments'], post['id'], 0)

					post['org_name'] = page_name
					post['url'] = 'http://facebook.com/' + post['id']
					
					# Get hashtags
					if 'message' in post.keys():
						hash_info = self.get_hashtags(post['message'])
						post['hashtags'] = hash_info[0]
						post['hashtags_count'] = hash_info[1]

					# Write Post to database
					new_entry = Post(post)
					self.session.merge(new_entry)

			time.sleep(sleep_time)
			print "Done."
			url = data['paging']['next']

	def get_hashtags(self, message):
		p = re.compile(r'#\w+')	
		matches = p.findall(message)
		return [', '.join(matches), len(matches)]

	def get_comments(self, comments, parent_id, count):
		count += len(comments['data'])
		for comment in comments['data']:

			# Get hashtags
			if 'message' in comment.keys():
				hash_info = self.get_hashtags(comment['message'])
				comment['hashtags'] = hash_info[0]
				comment['hashtags_count'] = hash_info[1]

			# Write Comment to database
			new_entry = Comment(comment, parent_id)
			self.session.merge(new_entry)
			self.session.commit()
		# Need to make a new json request for every 25 comments
		if 'paging' in comments.keys() and 'next' in comments['paging'].keys():
			comments = json.load(urllib2.urlopen(comments['paging']['next']))
			return self.get_comments(comments, parent_id, count)
		else:
			return count

	def print_debug(self, args, post):
		for arg in args:
			if arg in post.keys():
				print '{}: {}'.format(arg, post[arg])
		print ''

	def main(self):
		page_name = 'feedthechildren'
		pages = 100
		limit = 100
		sleep_time = 3
		fields = ['id', 'created_time', 'shares', 'type', 'likes.summary(true)', 
		             'comments{like_count,message,created_time}', 'message', 'link', 'status_type']

		self.get_page(page_name, pages, fields, limit, sleep_time)


if __name__ == "__main__":
	s = Scrape()
	s.main()