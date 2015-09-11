import json
import urllib2
import time
import re
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
from db_setup import Post, Comment


class Scrape:
	def __init__(self):
		engine = create_engine('sqlite:///fb-scraper.db', echo=False)
		Session = sessionmaker(bind=engine)
		self.session = Session()
		self.main()

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

	def get_page(self, page_name, fields, limit, sleep_time, since, until):
		'''Get Facebook page info'''
		access_token = self.fetch_app_access_token('1018392914858570', '72cf8c8a02b6e9315a11d7f0d714841d')
		url = 'https://graph.facebook.com/{0}/feed?access_token={1}&fields={2}&limit={3}&since={4}&until={5}'.format(page_name, access_token, ','.join(fields), limit, since, until)
		print url
		post_num = 1
		while url is not None:
			print '\nGETTING {2} POSTS {0} THROUGH {1}...'.format(post_num, post_num+limit-1, page_name)		

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
						post['comment_order'] = post['comments']['summary']['order']

					post['org_name'] = page_name
					post['url'] = 'http://facebook.com/' + post['id']
					
					# Get hashtags
					if 'message' in post.keys():
						hash_info = self.get_hashtags(post['message'])
						post['hashtags'] = hash_info[0]
						post['hashtags_count'] = hash_info[1]

					# Get mentions in each post
					if 'message_tags' in post.keys():
						mentions_info = self.get_mentions(post['message_tags'], kind='post')
						post['mentions'] = ', '.join(mentions_info)
						post['mentions_count'] = len(mentions_info)



					# Write Post to database
					new_entry = Post(post)
					self.session.merge(new_entry)

			time.sleep(sleep_time)
			print "Done."

			if 'paging' in data:
				url = data['paging']['next']
				post_num += limit
				print url
			else:
				url = None
		print "\n Finished downloading data."

	def get_mentions(self, message_tags, kind):
		mentions = []
		if kind == 'post':
			for mention in message_tags:
				mentions.append(message_tags[mention][0]['name'])
			return mentions
		elif kind == 'comment':
			for x, mention in enumerate(message_tags):
				mentions.append(message_tags[x]['name'])
			return mentions


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

			# Get mentions in each comment
			if 'message_tags' in comment.keys():
				mentions_info = self.get_mentions(comment['message_tags'], kind='comment')
				comment['mentions'] = ', '.join(mentions_info)
				comment['mentions_count'] = len(mentions_info)

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

	def date_unix(self, s):
		return time.mktime(datetime.datetime.strptime(s, "%d/%m/%Y").timetuple())

	def main(self):
		page_name = 'FeedingAmerica'
		limit = 25
		sleep_time = 3
		since = '1/1/2011' # dd/mm/yyyy
		until =  '23/3/2011' # dd/mm/yy
		fields = ['id', 'created_time', 'shares', 'type', 'likes.summary(true)', 
		             'comments.summary(true){like_count,message,created_time,from,message_tags}', 'message', 'link', 
		             'status_type', 'message_tags']

		self.get_page(page_name, fields, limit, sleep_time, self.date_unix(since), self.date_unix(until))


if __name__ == "__main__":
	s = Scrape()
	
