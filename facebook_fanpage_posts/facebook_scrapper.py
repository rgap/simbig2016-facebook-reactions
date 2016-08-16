import re
import urllib2
import urllib
import json
import time
import datetime
from dateutil.relativedelta import relativedelta

class FacebookScrapper:

	GRAPH_URL = "https://graph.facebook.com/"
	DB_POST_ATRIBUTES = ["id", "fb_id", "message", "likes_count", "time_created", "shares", "fanpagelink", "type", \
				"link", "name", "description", "external_picture", "num_comments", "page_id"]
	DB_COMMENT_ATRIBUTES = ["id", "fb_id", "message", "likes_count", "time_created", "post_id"]


	def __init__(self, APP_SECRET, APP_ID):

		self.APP_SECRET = APP_SECRET
		self.APP_ID = APP_ID

	def render_to_json(self, json_url):
		#render graph url call to JSON
		# Try three times to make contact
		tries = 1
		while True:
			try:
				web_response = urllib2.urlopen(json_url, timeout=10)
				readable_page = web_response.read()
				json_data = json.loads(readable_page)
				return json_data

			except:
				tries += 1
				print "trying again..."
				if tries >= 3:
					print 'Fatal error: urllib2 - Repeated timeouts'
					exit()

	def get_likes_count(self, post_id):
		if post_id == "":
			return ""
		likes_url = ""
		try:
			#create Graph API Call
			likes_args = post_id + "/likes?summary=true&key=value&access_token" + self.APP_ID + "|" + self.APP_SECRET
			likes_url = self.GRAPH_URL + likes_args
			likes_json = self.render_to_json(likes_url)
			#pick out the likes count
			count_likes = likes_json["summary"]["total_count"]
			return count_likes
		except:
			print "exception: get_likes_count"
			print likes_url
			return ""

	def create_post_url(self, company): 
		#create authenticated post URL
		post_args = "/posts/?key=value&access_token=" + self.APP_ID + "|" + self.APP_SECRET
		post_url = self.GRAPH_URL + company + post_args

		return post_url

	def get_picture_url(self, url):
		try:
			url_parsed = urlparse.parse_qs(urlparse.urlparse(url).query)["url"]
			return re.sub(r'\\(.)', r'\1', urllib.unquote_plus(url_parsed.decode('unicode_escape')))
		except:
			return ""
		finally:
			return url

	def get_fanpagelink(self, company, post_id):
		if post_id == "":
			return ""
		s_post_id = post_id[post_id.index('_') + 1:]

		return "https://www.facebook.com/" + company + "/posts/" + s_post_id

	def get_elementvalue(self, element, keys):
		try:
			if type(keys) in (tuple, list):
				elementvalue = element
				for key in keys:
					elementvalue = elementvalue[key]
				return elementvalue
			else:
				return element[keys]
		except:
			pass
		return ""

	def scrape_posts_by_date(self, post_url, date, posts, company):

		try:
			#render URL to JSON
			json_data = self.render_to_json(post_url)
			page_posts = json_data["data"]

			#for each post capture data
			for post in page_posts:
				fb_post_id 			= self.get_elementvalue(post, "id")
				message 			= self.get_elementvalue(post, "message")
				likes_count 		= self.get_likes_count(fb_post_id)
				time_created 		= self.get_elementvalue(post, "created_time")
				shares 				= self.get_elementvalue(post, ["shares", "count"])
				fanpagelink 		= self.get_fanpagelink(company, fb_post_id)
				post_type 			= self.get_elementvalue(post, "type")
				link 				= self.get_elementvalue(post, "link")
				name 				= self.get_elementvalue(post, "name")
				description 		= self.get_elementvalue(post, "description")
				external_picture 	= self.get_picture_url(self.get_elementvalue(post, "picture"))
				num_comments 		= self.get_num_comments(fb_post_id)

				current_post = [fb_post_id, message, likes_count, time_created, shares, fanpagelink, 
							post_type, link, name, description, external_picture, num_comments]

				if date <= time_created:
					posts.append(current_post)
					print "scrapping post # " + str(len(posts))
				else:
					return posts

		except Exception:
			print 'Fatal error: after scrapping posts - scrape_posts_by_date'
			exit()

		try:
			#extract next page
			next_page = json_data["paging"]["next"]
			print "next page = " + next_page
			self.scrape_posts_by_date(next_page, date, posts, company)
		except:
			print "no more posts"
			return


	def create_comments_url(self, post_id):
		comments_args = post_id + "/comments/?key=value&summary=true&access_token=" + self.APP_ID + "|" + self.APP_SECRET
		comments_url = self.GRAPH_URL + comments_args
		return comments_url

	def get_num_comments(self, post_id):
		if post_id == "":
			return ""
		try:
			comments_url = self.create_comments_url(post_id)
			return self.render_to_json(comments_url)["summary"]["total_count"]
		except:
			print "exception: get_num_comments"
			print comments_url
			return ""



	def get_comments_data(self, comments_url, comments, post_id):

		try:
			#render URL to JSON
			json_data = self.render_to_json(comments_url)
			post_comments = json_data["data"]
			#for each comment capture data
			for comment in post_comments:
				comment_id 				= self.get_elementvalue(comment, "id")
				comment_message 		= self.get_elementvalue(comment, "message")
				comment_like_count 		= self.get_elementvalue(comment, "like_count")
				comment_created_time 	= self.get_elementvalue(comment, "created_time")
				current_comment = [comment_id, comment_message, comment_like_count,
									comment_created_time, post_id]
				comments.append(current_comment)

			print "scrapping comments "
			#extract next page
			next_page = json_data["paging"]["next"]
			print "next page"
			self.get_comments_data(next_page, comments, post_id)

		except Exception:
			return 

	def get_page_info(self, company):
		#open public page in facebook graph api
		fbpage = self.render_to_json(self.GRAPH_URL + company)
		#gather our page level JSON Data
		return [self.get_elementvalue(fbpage, "id"), self.get_elementvalue(fbpage, "likes"),
				self.get_elementvalue(fbpage, "talking_about_count"), self.get_elementvalue(fbpage, "username"),
				self.get_elementvalue(fbpage, "about"), self.get_elementvalue(fbpage, "description")]
