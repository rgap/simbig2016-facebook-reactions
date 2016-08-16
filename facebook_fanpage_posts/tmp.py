import re
import urllib2
import urllib
import json
import time
import datetime
import csv
from dateutil.relativedelta import relativedelta
from facebook_scrapper import FacebookScrapper
from buzzfeed.post_metadata import PostMetadata

def main():

	#the time of last weeks crawl
	last_crawl = datetime.datetime.now() - relativedelta(years=200)
	last_crawl = last_crawl.isoformat()
	print "scrapping facebook"

	info_file = open('data/info.txt', 'w')
	json_data = []
	json_file = open("data/buzzfeed_data.json", "w")

	header = FacebookScrapper.POST_ATRIBUTES
	post_metadata = PostMetadata()
	post_metadata.append_metadata_header(header)

	#simple data pull App Secret and App ID
	APP_SECRET = "d0392c193d358754c3d69dd49aa0a690"
	APP_ID = "1671034626459190"
	fc = FacebookScrapper(APP_SECRET, APP_ID)

	for company in list_companies:

		#extract post data
		post_url = fc.create_post_url(company)
		posts = []
		fc.scrape_posts_by_date(post_url, last_crawl, posts, company)

		info_file.write(company + ' : ' + str(len(posts)) + ' posts \n')
		info_file.close()

		#loop through and insert posts
		for i, post in enumerate(posts):

			print "storing post " + str(i) + " data......... " + post[0]
			#append additional metadata
			post_metadata.append_metadata_element(post)

			row = dict(zip(header, post))
			json_data.append(row)

		json.dump(json_data, json_file)
	json_file.close()


if __name__ == "__main__":
	main()