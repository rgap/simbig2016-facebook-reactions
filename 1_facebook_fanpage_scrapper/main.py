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

    def __init__(self):
        # Fill this out with your db connection info
        self.connection = mysql.connector. \
                          connect(user='root', password='1',
                                  host='localhost',
                                  database='facebook_fanpage_unilad')
        self.cursor = self.connection.cursor()

        self.query_selectid_page = ("SELECT id FROM page WHERE fb_id = %s")
        # SQL statement for adding Facebook page data to database
        self.query_insert_page = ("INSERT INTO page "
                                  "(fb_id, likes, talking_about, "
                                  "username, about, description) "
                                  "VALUES (%s, %s, %s, %s, %s, %s)")

        self.query_selectid_post = ("SELECT id FROM post WHERE fb_id = %s")
        # SQL statement for adding post data
        self.query_insert_post = ("INSERT INTO post "
                                  "(fb_id, message, likes_count, "
                                  "time_created, shares, fanpagelink, type, "
                                  "link, name, description, external_picture, "
                                  "num_comments, page_id)"
                                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, "
                                  "%s, %s, %s, %s, %s)")

        self.query_selectid_comment = ("SELECT id FROM comment "
                                       "WHERE fb_id = %s")
        # SQL statement for adding comment data
        self.query_insert_comment = ("INSERT INTO comment "
                                     "(fb_id, message, likes_count, "
                                     "time_created, post_id)"
                                     "VALUES (%s, %s, %s, %s, %s)")

    def close(self):
        print("connection closed")
        self.connection.close()

    def commit(self):
        print("data committed")
        # Commit the data to the db
        self.connection.commit()

    def insert_info(self, page):
        try:
            self.cursor.execute(self.query_insert_page, page)
            return self.cursor.lastrowid
        except:
            while True:
                try:
                    self.cursor.execute(self.query_selectid_page, [page[0]])
                    print("insert_info already exists")
                    return self.cursor.fetchone()[0]
                except:
                    print("no mysql connection")
                    pass

    def insert_post(self, post):
        try:
            self.cursor.execute(self.query_insert_post, post)
            return self.cursor.lastrowid
        except:
            while True:
                try:
                    self.cursor.execute(self.query_selectid_post, [post[0]])
                    print("insert_post already exists")
                    return self.cursor.fetchone()[0]
                except:
                    print("no mysql connection")
                    pass

    def insert_comment(self, comment):
        try:
            self.cursor.execute(self.query_insert_comment, comment)
            return self.cursor.lastrowid
        except:
            while True:
                try:
                    self.cursor.execute(self.query_selectid_comment,
                                        [comment[0]])
                    print("insert_comment already exists")
                    return self.cursor.fetchone()[0]
                except:
                    print("no mysql connection")
                    pass

    def get_posts(self):
        self.cursor.execute("SELECT * FROM post")
        return self.cursor.fetchall()


def main():

    # To find go to page's FB page, at the end of URL find username
    # E.g. http://facebook.com/walmart, walmart is the username
    list_companies = ["uniladmag"]

    # Save all comments
    save_comments = False
    # Max number of posts
    max_posts = 10

    # The time of last weeks crawl
    last_crawl = datetime.datetime.now() - relativedelta(years=200)
    last_crawl = last_crawl.isoformat()

    db_connection = DBConnection()

    # Simple data pull App Secret and App ID
    APP_SECRET = "28578690baddda5067c19cd7b7c9446e"
    APP_ID = "1443249892642264"
    fc = FacebookScrapper(APP_SECRET, APP_ID)

    # Get posts already in database
    db_posts_dict = {}
    db_posts = db_connection.get_posts()
    get_db_posts(db_posts_dict, db_posts)

    for company in list_companies:

        # Make graph api url with company username
        page = fc.get_page_info(company)
        # Insert the data we pulled into db and commit
        page_id = db_connection.insert_info(page)
        db_connection.commit()

        # Extract post data
        post_url = fc.create_post_url(company)
        posts = []
        print(post_url)
        fc.scrape_posts_by_date(post_url, last_crawl,
                                posts, company, db_posts_dict, max_posts)

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

        # Commit the data to the db
        db_connection.commit()
    db_connection.close()

if __name__ == "__main__":
    main()
