import re
import urllib2
import urllib
import json
import time
import datetime
import csv
import mysql.connector
import numpy as np
from dateutil.relativedelta import relativedelta
from buzzfeed.post_metadata import PostMetadata, date_handler
from facebook_scrapper import FacebookScrapper

def get_posts_from_mysql():
    connection = mysql.connector.connect(user='root', password='1',
                                        host = 'localhost',
                                        database='facebook_fanpage_buzzfeed')
    cursor = connection.cursor()
    # First the most recent ones
    cursor.execute("SELECT * FROM post ORDER BY time_created DESC")
    return cursor.fetchall()


def get_db_posts(json_data_path, json_done_data_path):
    db_posts = []
    db_done_posts = {}
    try:
        file_json = open(json_data_path, "rb")
        db_posts = json.load(file_json)
        done_json = open(json_done_data_path, "rb")
        db_done_posts = json.load(done_json)

    except:
        pass #there was no previous data
    finally:
        print "There were " + str(len(db_posts)) + " posts"
        print "And " + str(len(db_done_posts)) + " done posts"
        return db_posts, db_done_posts


def main():

    info_file = open('data/info.txt', 'w')
    json_data_path = "data/buzzfeed_data.json"
    json_done_data_path = "data/buzzfeed_done_data.json"

    #get posts already in database
    db_posts, db_done_posts = get_db_posts(json_data_path, json_done_data_path)

    #get posts from mysql
    header = FacebookScrapper.DB_POST_ATRIBUTES
    post_metadata = PostMetadata()
    post_metadata.append_metadata_header(header)
    posts = get_posts_from_mysql()

    #loop through and insert posts
    counter = 0
    for post in posts:
        if counter >= 200:
            print "Avoiding socket.error: [Errno 10054] An existing \connection was forcibly closed by the remote host"
            break

        post = list(post)
        if post[header.index("fb_id")] in db_done_posts: # verify if its already in database
            continue

        print "--------------------- NEW POST ---------------------"
        #append additional metadata
        scrapper_result = post_metadata.append_metadata_element(post)
        if scrapper_result == "L":
            db_done_posts[post[1]] = 1
            continue

        # fb_id
        db_done_posts[post[1]] = 1

        if scrapper_result == "NO_REACTION":
            continue

        print "storing post # " + str(len(db_posts) + 1)
        row = dict(zip(header, post))
        db_posts.append(row)
        counter += 1

    # storing data on json file
    json_file = open(json_data_path, "w")
    json.dump(db_posts, json_file, default=date_handler)
    json_file.close()

    # storing done processed data
    json_file = open(json_done_data_path, "w")
    json.dump(db_done_posts, json_file, default=date_handler)
    json_file.close()


if __name__ == "__main__":
    main()
