#coding=utf-8 
#!/usr/bin/python

import os
import sys
import json
import time
import urllib2
import re
import copy
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
from sc_utils import ScrapperUtils as SC

class BuzzfeedScrapperUrllib:

    reaction_names_template = ["acamazing", "fail", "wtf", "lol", "trashy", "win", "ew", \
                "omg", "cute", "yaaass", "love", "hate", "drab", "blimey", "fab", "ohdear", "splendid"]

    reaction_counter_dict_template = {}

    def __init__(self):
        i = 0
        for reaction in self.reaction_names_template:
            self.reaction_counter_dict_template[reaction] = i
            i += 1
        self.response = ""

    def get_text_json_value(self, text_json, key):

        value = ""
        pos_key = text_json.find(key)
        if pos_key == -1:
            return value

        getting_value = False
        pos_ini = text_json.find(key) + len(key) + 1
        for i in range(pos_ini, len(text_json)):
            if getting_value == False:
                if text_json[i] != '\"':
                    continue
                else:
                    getting_value = True
                    continue
            if text_json[i] != '\"':
                value += text_json[i]
            else:
                return value

    def savetag_reaction_counter_array(self, soup):

        reaction_counter_template = [0] * len(self.reaction_names_template)

        f = open("web_post.txt", "w")
        f.write(str(soup))
        f.close()

        try:
            reactions_container = SC.get_tag(soup, "div", {"id": "reactions_wrapper"})
            slidertag = SC.get_tag(reactions_container, "div", class_="reaction-badges__slider")
            reactions_ul = SC.get_tag(slidertag, "ul")
            reactions_data = reactions_ul.findAll("div", class_="reaction")

            for reaction_data in reactions_data: 
                reaction_text_json = reaction_data["reaction_data"]
                reaction_name = self.get_text_json_value(reaction_text_json, "name")
                count_str = self.get_text_json_value(reaction_text_json, "count")
                count = "0" if (count_str == '' or not count_str) else count_str

                if reaction_name in self.reaction_names_template:
                    reaction_counter_template[self.reaction_counter_dict_template[reaction_name]] = int(count)
        except:
            reaction_counter_template = []
        finally:
            return reaction_counter_template

    def get_post_data(self, url, web_elements):

        if not SC.page_loaded_urllib(self, url):
            return "L"

        html_source = self.response.read()
        soup = BeautifulSoup(html_source)

        ######################### getting reaction_counter_array
        if 'reaction_counter_array' in web_elements:
            reaction_counter_array = self.savetag_reaction_counter_array(soup)
            web_elements['reaction_counter_array'] = reaction_counter_array
            
            