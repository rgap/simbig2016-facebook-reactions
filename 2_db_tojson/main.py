#!/usr/bin/env python

import json
import mysql.connector
from facebook_scrapper import FacebookScrapper


def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj


def get_posts_from_mysql(db_user, db_password, hostname, database):
    connection = mysql.connector. \
                      connect(user=db_user, password=db_password,
                              host=hostname, database=database)
    cursor = connection.cursor()
    print(database)
    # First the most recent ones
    cursor.execute("SELECT * FROM post ORDER BY time_created DESC")
    return cursor.fetchall()


def check_has_reactions(row):
    reaction_columns = ["fb_love", "fb_wow", "fb_haha", "fb_sad",
                        "fb_angry", "fb_thankful"]
    for column in reaction_columns:
        if row[column] != 0:
            return True
    return False


def main():

    # Load configuration file
    configs_path = "configs.json"
    with open(configs_path, "r") as configs_file:
        configs = json.loads(configs_file.read())["paths"]

    db_posts = []
    for config in configs:
        with open(config, "r") as config_file:
            mysql_config = json.loads(config_file.read())

        posts = get_posts_from_mysql(mysql_config["db_user"],
                                     mysql_config["db_password"],
                                     mysql_config["hostname"],
                                     mysql_config["database"])

        # Get posts from mysql
        header = FacebookScrapper.DB_POST_ATRIBUTES
        header.append("database")
        for post in posts:
            row = dict(zip(header, post))
            row["database"] = mysql_config["database"]
            if(row["type"] == "link" and check_has_reactions(row)):
                db_posts.append(row)

    print("%s posts" % len(db_posts))
    json_data_path = "data/facebook_pages_data.json"
    json_file = open(json_data_path, "w")
    json.dump(db_posts, json_file, default=date_handler)
    json_file.close()

if __name__ == "__main__":
    main()
