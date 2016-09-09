import re
import json
import sys
from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.parse import unquote_plus


class FacebookScrapper:

    GRAPH_URL = "https://graph.facebook.com/"
    DB_POST_ATRIBUTES = ["id", "fb_id", "message", "fb_like", "fb_love",
                         "fb_wow", "fb_haha", "fb_sad", "fb_angry",
                         "fb_thankful", "time_created", "shares",
                         "fanpagelink", "type", "link", "name", "description",
                         "external_picture", "num_comments", "page_id"]
    DB_COMMENT_ATRIBUTES = ["id", "fb_id", "message", "fb_like",
                            "time_created", "post_id"]

    def __init__(self, APP_SECRET, APP_ID):

        self.APP_SECRET = APP_SECRET
        self.APP_ID = APP_ID

    def render_to_json(self, json_url):
        # Render graph url call to JSON
        # Try three times to make contact
        tries = 1
        while tries <= 20:
            try:
                web_response = urlopen(json_url, timeout=50)
                readable_page = web_response.read()
                json_data = json.loads(readable_page.decode("utf-8"))
                return json_data

            except:
                print("trying again... " + str(tries))
                print(json_url)
                tries += 1

        key = input("Probably the number of requests was exceeded, "
                    "(1) stop, (2) keep trying : ")
        if key == "1":
            print("stop")
            return "L"
        if key == "2":
            print("keep trying")
            self.render_to_json(json_url)

    def get_reactions_count(self, post_id):
        if post_id == "":
            return ""
        likes_url = ""
        try:
            # Create Graph API Call
            args = (
                "v2.7?id=" + post_id +
                "&fields="
                "reactions.type(LIKE).limit(0).summary(total_count)"
                ".as(reactions_like),"
                "reactions.type(LOVE).limit(0).summary(total_count)"
                ".as(reactions_love),"
                "reactions.type(WOW).limit(0).summary(total_count)"
                ".as(reactions_wow),"
                "reactions.type(HAHA).limit(0).summary(total_count)"
                ".as(reactions_haha),"
                "reactions.type(SAD).limit(0).summary(total_count)"
                ".as(reactions_sad),"
                "reactions.type(ANGRY).limit(0).summary(total_count)"
                ".as(reactions_angry),"
                "reactions.type(THANKFUL).limit(0).summary(total_count)"
                ".as(reactions_thankful)" +
                "&access_token=" + self.APP_ID + "|" + self.APP_SECRET)

            likes_url = self.GRAPH_URL + args
            likes_json = self.render_to_json(likes_url)
            if self.request_limit_reached(likes_json):
                return "L"

            # Pick out the counters
            c = [0] * 7
            c[0] = likes_json["reactions_like"]["summary"]["total_count"]
            c[1] = likes_json["reactions_love"]["summary"]["total_count"]
            c[2] = likes_json["reactions_wow"]["summary"]["total_count"]
            c[3] = likes_json["reactions_haha"]["summary"]["total_count"]
            c[4] = likes_json["reactions_sad"]["summary"]["total_count"]
            c[5] = likes_json["reactions_angry"]["summary"]["total_count"]
            c[6] = likes_json["reactions_thankful"]["summary"]["total_count"]
            return c
        except:
            print("exception: get_reactions_count - leaving it with 0s")
            print(likes_json)
            print(likes_url)
            return c

    def create_post_url(self, company):
        # Create authenticated post URL
        post_args = ("/posts/?key=value"
                     "&access_token=" + self.APP_ID + "|" + self.APP_SECRET)
        post_url = self.GRAPH_URL + company + post_args

        return post_url

    def get_picture_url(self, url):
        try:
            url_parsed = urlparse.parse_qs(urlparse.urlparse(url).query)["url"]
            return re.sub(r'\\(.)', r'\1',
                          unquote_plus(
                            url_parsed.decode('unicode_escape')))
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

    def request_limit_reached(self, json_data):
        if json_data == "L":
            return True
        try:
            error = json_data["error"]
            print(error["message"])
            return True
        except:
            return False

    def scrape_posts_by_date(self, post_url, date, posts, company,
                             db_posts_dict, max_posts):
        # Save last posts url
        with open('last_post_url.txt', 'w') as lastpost_file:
            lastpost_file.write(post_url)
        # Render URL to JSON
        json_data = self.render_to_json(post_url)

        if self.request_limit_reached(json_data):
            return

        try:
            page_posts = json_data["data"]
        except:
            print("fanpage updated, cannot get more posts")
            return

        try:
            # For each post capture data
            for post in page_posts:
                fb_post_id = self.get_elementvalue(post, "id")
                if fb_post_id in db_posts_dict:
                    print("post was already in database")
                    continue

                message = self.get_elementvalue(post, "message")
                time_created = self.get_elementvalue(post, "created_time")
                shares = self.get_elementvalue(post, ["shares", "count"])
                fanpagelink = self.get_fanpagelink(company, fb_post_id)
                post_type = self.get_elementvalue(post, "type")
                link = self.get_elementvalue(post, "link")
                print(fanpagelink)
                name = self.get_elementvalue(post, "name")
                description = self.get_elementvalue(post, "description")
                external_picture = self.get_picture_url(
                                        self.get_elementvalue(post, "picture"))
                num_comments = self.get_num_comments(fb_post_id)
                if num_comments == "L":
                    return

                counter = self.get_reactions_count(fb_post_id)
                if counter == "L":
                    return
                fb_like = counter[0]
                fb_love = counter[1]
                fb_wow = counter[2]
                fb_haha = counter[3]
                fb_sad = counter[4]
                fb_angry = counter[5]
                fb_thankful = counter[6]

                current_post = [fb_post_id, message, fb_like, fb_love,
                                fb_wow, fb_haha, fb_sad, fb_angry,
                                fb_thankful, time_created, shares,
                                fanpagelink, post_type, link, name,
                                description, external_picture, num_comments]

                len_posts = len(posts)
                if len_posts < max_posts and date <= time_created:
                    posts.append(current_post)
                    print("post # " + str(len_posts))
                else:
                    return

        except Exception:
            print("fatal error: after getting posts - scrape_posts_by_date")
            return

        try:
            # Extract next page
            next_page = json_data["paging"]["next"]
            print("next page = " + next_page)
            self.scrape_posts_by_date(next_page, date, posts, company,
                                      db_posts_dict, max_posts)
        except:
            print("no more posts")
            return

    def create_comments_url(self, post_id):
        comments_args = (post_id + "/comments/?key=value&summary=true"
                         "&access_token=" +
                         self.APP_ID + "|" + self.APP_SECRET)
        comments_url = self.GRAPH_URL + comments_args
        return comments_url

    def get_num_comments(self, post_id):
        if post_id == "":
            return ""
        try:
            comments_url = self.create_comments_url(post_id)
            comments_json = self.render_to_json(comments_url)
            if self.request_limit_reached(comments_json):
                return "L"
            if not comments_json["data"] == []:
                return comments_json["summary"]["total_count"]
            else:
                return 0
        except:
            print("exception: get_num_comments")
            print(comments_url)
            return 0

    def get_comments_data(self, comments_url, comments, post_id):

        try:
            # Render URL to JSON
            json_data = self.render_to_json(comments_url)
            if self.request_limit_reached(json_data):
                return "L"

            post_comments = json_data["data"]
            # For each comment capture data
            for comment in post_comments:
                comment_id = (
                            self.get_elementvalue(comment, "id"))
                comment_message = (
                            self.get_elementvalue(comment, "message"))
                comment_fb_like = (
                            self.get_elementvalue(comment, "fb_like"))
                comment_created_time = (
                            self.get_elementvalue(comment, "created_time"))
                current_comment = [comment_id, comment_message,
                                   comment_fb_like, comment_created_time,
                                   post_id]
                comments.append(current_comment)

            print("comments # " + str(len(comments)))
            # Extract next page
            next_page = json_data["paging"]["next"]
            print("next page")
            self.get_comments_data(next_page, comments, post_id)

        except Exception:
            return

    def get_page_info(self, company):
        # Open public page in facebook graph api
        fbpage = self.render_to_json(self.GRAPH_URL + company +
                                     "?access_token=" +
                                     self.APP_ID + "|" + self.APP_SECRET)
        if self.request_limit_reached(fbpage):
            sys.exit(0)
        # Gather our page level JSON Data
        return [self.get_elementvalue(fbpage, "id"),
                self.get_elementvalue(fbpage, "likes"),
                self.get_elementvalue(fbpage, "talking_about_count"),
                self.get_elementvalue(fbpage, "username"),
                self.get_elementvalue(fbpage, "about"),
                self.get_elementvalue(fbpage, "description")]
