from buzzfeed_scrapper_urllib import BuzzfeedScrapperUrllib

def date_handler(obj):
	return obj.isoformat() if hasattr(obj, 'isoformat') else obj

class PostMetadata:
	"""
	Class that stores metadata
	"""

	def __init__(self):
		"""
		initialize buzzfeed metadata
		"""
		
		self.scrapper = BuzzfeedScrapperUrllib()
		self.element = 'reaction_counter_array'

	def append_metadata_header(self, header):
		for key in BuzzfeedScrapperUrllib.reaction_names_template:
			header.append(key)

	def append_metadata_element(self, post):

		if post[8] != "" and (not ("http://www.hipsterrunoff.com/" in post[8])) and (not ("http://searchassist.verizon.com/" in post[8])) and (not ("https://www.facebook.com/" in post[8])) and (not ("http://www.youtube.com/" in post[8])) and (not ("http://instagram.com/" in post[8])) and (not ("http://instagr.am/" in post[8])): #link
			print post[8]
			web_elements = {self.element: None}
			if self.scrapper.get_post_data(post[8], web_elements) == "L":
				return "L"

			if web_elements[self.element] == []:
				print "Post didn't have a reaction counter"
				return "NO_REACTION"
			else:
				for value in web_elements[self.element]:
					post.append(value)
		else:
			print "Post not redirecting to it's website"
			return "NO_REACTION"
