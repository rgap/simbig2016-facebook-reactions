#!/usr/bin/env python
"""Facebook fanpage scrapper

Usage:
    main.py <max_posts> <config_path> [--continue]

Arguments:
    max_posts       maximum number of posts to get
    config_path     configuration file
    --continue      to continue scrapping since last post,
                    the file  containing this last post' url
                    is at tmp/lastpost_<DATASETNAME>.txt'
"""

import os
import sys
import json
import mysql.connector
import datetime
from dateutil.relativedelta import relativedelta
from facebook_scrapper import FacebookScrapper


def get_db_posts(db_posts_dict, db_posts):

    for post in db_posts:
        db_posts_dict[
            post[FacebookScrapper.DB_POST_ATRIBUTES.index("fb_id")]
        ] = 1


class DBConnection:

    def __init__(self, db_user, db_password, hostname, database):
        # Fill this out with your db connection info
        self.db_user = db_user
        self.db_password = db_password
        self.hostname = hostname
        self.database = database

        self.query_selectid_page = ("SELECT id FROM page WHERE fb_id = %s")
        # SQL statement for adding Facebook page data to database
        self.query_insert_page = ("INSERT INTO page "
                                  "(fb_id, fb_like, talking_about, "
                                  "username, about, description) "
                                  "VALUES (%s, %s, %s, %s, %s, %s)")

        self.query_selectid_post = ("SELECT id FROM post WHERE fb_id = %s")
        # SQL statement for adding post data
        self.query_insert_post = ("INSERT INTO post "
                                  "(fb_id, message, fb_like, "
                                  "fb_love, fb_wow, fb_haha, "
                                  "fb_sad, fb_angry, fb_thankful, "
                                  "time_created, shares, fanpagelink, type, "
                                  "link, name, description, external_picture, "
                                  "num_comments, page_id) "
                                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, "
                                  "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                                  )

        self.query_selectid_comment = ("SELECT id FROM comment "
                                       "WHERE fb_id = %s")
        # SQL statement for adding comment data
        self.query_insert_comment = ("INSERT INTO comment "
                                     "(fb_id, message, fb_like, "
                                     "time_created, post_id)"
                                     "VALUES (%s, %s, %s, %s, %s)")

    def connect(self):
        self.connection = mysql.connector. \
                          connect(user=self.db_user, password=self.db_password,
                                  host=self.hostname, database=self.database)
        self.cursor = self.connection.cursor()
        print("connection established")

    def close(self):
        self.connection.close()
        print("connection closed")

    def commit(self):
        # Commit the data to the db
        self.connection.commit()
        print("data committed")

    def insert_info(self, page):
        try:
            self.cursor.execute(self.query_insert_page, page)
            return self.cursor.lastrowid
        except:
            tries = 1
            while tries <= 20:
                try:
                    self.cursor.execute(self.query_selectid_page, [page[0]])
                    print("insert_info already exists")
                    return self.cursor.fetchone()[0]
                except mysql.connector.Error as e:
                    print("Something went wrong - insert_info: {}".format(e))
                    print("trying again... " + str(tries))
                    tries += 1
                    pass
        key = input("Probably lost connection with mysql "
                    "(1) stop, (2) keep trying : ")
        if key == "1":
            print("stop")
            sys.exit()
        if key == "2":
            print("keep trying")
            self.insert_info(page)

    def insert_post(self, post):
        try:
            self.cursor.execute(self.query_insert_post, post)
            return self.cursor.lastrowid
        except mysql.connector.Error as e:
            print("Not inserted: {}".format(e))
            tries = 1
            while tries <= 20:
                try:
                    self.cursor.execute(self.query_selectid_post, [post[0]])
                    print("insert_post already exists")
                    return self.cursor.fetchone()[0]
                except mysql.connector.Error as e:
                    print("Something went wrong - insert_post: {}".format(e))
                    print("trying again... " + str(tries))
                    tries += 1
                    pass
        key = input("Probably lost connection with mysql "
                    "(1) stop, (2) keep trying : ")
        if key == "1":
            print("stop")
            sys.exit()
        if key == "2":
            print("keep trying")
            self.insert_post(post)

    def insert_comment(self, comment):
        try:
            self.cursor.execute(self.query_insert_comment, comment)
            return self.cursor.lastrowid
        except:
            tries = 1
            while tries <= 20:
                try:
                    self.cursor.execute(self.query_selectid_comment,
                                        [comment[0]])
                    print("insert_comment already exists")
                    return self.cursor.fetchone()[0]
                except mysql.connector.Error as e:
                    print("Something went wrong - insert_comment: {}".
                          format(e))
                    print("trying again... " + str(tries))
                    tries += 1
                    pass
        key = input("Probably lost connection with mysql "
                    "(1) stop, (2) keep trying : ")
        if key == "1":
            print("stop")
            sys.exit()
        if key == "2":
            print("keep trying")
            self.insert_comment(comment)

    def get_posts(self):
        self.cursor.execute("SELECT * FROM post")
        return self.cursor.fetchall()


def main(args):

    # Max number of posts
    max_posts = int(args['<max_posts>'])
    config_path = args['<config_path>']
    continue_flag = args["--continue"]

    # Load configuration file
    with open(config_path) as config_file:
        config = json.loads(config_file.read())

    # To find go to page's FB page, at the end of URL find username
    # E.g. http://facebook.com/walmart, walmart is the username
    list_companies = [config["fb_fanpage_name"]]

    # Save all comments
    save_comments = False

    # The time of last weeks crawl
    last_crawl = datetime.datetime.now() - relativedelta(years=200)
    last_crawl = last_crawl.isoformat()

    # Configure connection and connect
    db_connection = DBConnection(config["db_user"],
                                 config["db_password"],
                                 config["hostname"],
                                 config["database"])
    db_connection.connect()

    # Simple data pull App Secret and App ID
    APP_SECRET = config["APP_SECRET"]
    APP_ID = config["APP_ID"]
    fc = FacebookScrapper(APP_SECRET, APP_ID)

    # Get posts already in database
    db_posts_dict = {}
    db_posts = db_connection.get_posts()
    get_db_posts(db_posts_dict, db_posts)

    # Get last posts url
    post_url = ""
    lasturl_path = 'tmp/lasturl_%s.txt' % config["database"]
    if(continue_flag):
        if os.path.isfile(lasturl_path):
            with open(lasturl_path, 'r') as lastpost_file:
                post_url = lastpost_file.read()

    for company in list_companies:

        # Make graph api url with company username
        page = fc.get_page_info(company)
        # Insert the data we pulled into db, commit and close connection
        page_id = db_connection.insert_info(page)
        db_connection.commit()
        db_connection.close()

        posts = []
        # Extract post data
        if post_url == "":
            post_url = fc.create_post_url(company)
        print(post_url)
        fc.scrape_posts_by_date(post_url, last_crawl,
                                posts, company, db_posts_dict, max_posts,
                                lasturl_path)

        # Reconnect
        db_connection.connect()
        # Loop through and insert posts
        for post in posts:
            print("storing post data......... " + post[0])
            post.append(page_id)
            # Insert post and commit
            post_id = db_connection.insert_post(post)
            db_connection.commit()
            if save_comments:
                # Retrieving and saving comments
                comment_url = fc.create_comments_url(post[0])
                comments = []
                fc.get_comments_data(comment_url, comments, post_id)
                # Loop through and insert comments
                for comment in comments:
                    db_connection.insert_comment(comment)
                    db_connection.commit()
    db_connection.close()

if __name__ == "__main__":
    from docopt import docopt
    main(docopt(__doc__))
