#coding=utf-8 
#!/usr/bin/python

import os
import sys
import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
from sc_utils import ScrapperUtils as SC

class BuzzfeedScrapperSelenium:

	browser = None
	reaction_counter_dict_template = {"fail": "", "wtf": "", "lol": "", "trashy": "", "win": "", "ew": "", \
				"omg": "", "cute": "", "yaaass": "", "love": "", "hate": "", "drab": ""}

	def __init__(self):
		self.init_browser()

	def __del__(self):
		self.close_browser()

	def init_browser(self):
		self.browser = webdriver.Firefox()
		self.browser.set_page_load_timeout(10)
		#self.browser = webdriver.Chrome('/home/rgap/Installed/chromedriver')

	def close_browser(self):
		try:
			self.browser.close()
		except:
			"error - no browser"

	def savetag_post_title(self, soup):
		post_title = ""
		try:
			post_title_tag = SC.get_tag(soup, 'h1', {'id': 'post-title'})
			post_title = post_title_tag.getText()
			print (post_title)
		except NoSuchTagException:
			print ("No such tag on savetag_post_title")
		finally:
			return (post_title)

	def savetag_description(self, soup):
		description = ""
		try:
			description_tag = SC.get_tag(soup, "p", class_="description")
			description_b = SC.get_tag(description_tag, "b")
			description = description_b.getText()
		except NoSuchTagException:
			print ("No such tag on savetag_description")
		finally:
			return description

	def savetag_formattedtime(self, soup):
		formattedtime = ""
		try:
			datetext_span = SC.get_tag(soup, "span", class_="buzz_datetime")
			datetext = datetext_span.getText().replace('.', '')
			splitted = datetext.split()
			splitted[2] = splitted[2][:3]
			if splitted[0] != 'posted':
				return
			datetext_corrected = ' '.join(splitted)
			formattedtime = datetime.strptime(datetext_corrected,"posted on %b %d, %Y, at %I:%M %p").ctime()
		except NoSuchTagException:
			print ("No such tag on savetag_formattedtime")
		finally:
			return formattedtime

	def savetag_author_name(self, soup):
		author_name = ""
		try:
			author_tag = SC.get_tag(soup, "div", class_="byline__body")
			author_name = SC.get_tag(author_tag, "a").getText()
		except NoSuchTagException:
			print ("No such tag on savetag_author_name")
		finally:
			return author_name

	def savetag_reaction_counter_dict(self, soup):

		try:
			SC.wait_element(self.browser, "bar-wrapper")
			reactions_container = SC.get_tag(soup, "div", {"id": "reactions_wrapper"})
			slidertag = SC.get_tag(reactions_container, "div", class_="slider_wrapper")
			reactions_ul = SC.get_tag(slidertag, "ul")

			for li in reactions_ul.findAll('li'): 
				reaction_name = li.get('id')[9:]
				count_str = SC.get_tag(li, "div", class_="reaction-count").getText().replace(',', '')
				count = "0" if count_str == "" else count_str
				self.reaction_counter_dict_template[reaction_name] = int(count)
			print "found tag - savetag_reaction_counter_dict"
		except NoSuchTagException:
			print ("No such tag on savetag_reaction_counter_dict")
		finally:
			return self.reaction_counter_dict_template

	def get_post_data(self, url, web_elements):
		while True:
			if SC.page_loaded(self, url):
				break

		html_source = self.browser.page_source
		soup = BeautifulSoup(html_source)

		if 'url' in web_elements:
			web_elements = {}
			web_elements['url'] = url

		######################### getting post title
		if 'post_title' in web_elements:
			post_title = self.savetag_post_title(soup)
			web_elements['post_title'] = post_title

		######################### getting description
		if 'description' in web_elements:
			description = self.savetag_description(soup)
			web_elements['description'] = description

		######################### getting formatted time
		if 'formattedtime' in web_elements:
			formattedtime = self.savetag_formattedtime(soup)
			web_elements['formattedtime'] = formattedtime

		######################### getting author name
		if 'author_name' in web_elements:
			author_name = self.savetag_author_name(soup)
			web_elements['author_name'] = author_name

		######################### getting reaction_counter_dict
		if 'reaction_counter_dict' in web_elements:
			reaction_counter_dict = self.savetag_reaction_counter_dict(soup)
			print reaction_counter_dict
			web_elements['reaction_counter_dict'] = reaction_counter_dict
			