import praw
import config
import time
import requests
import sqlite3


def authenticate():
    print("Authenticating. . .")
    reddit = praw.Reddit(username = config.username,
                         password = config.password,
                         client_id = config.client_id,
                         client_secret = config.client_secret,
                user_agent = "joke comment responder")
    print("Authenticated!")
    return reddit


def run_bot(reddit, comments_replied_to):
    print("Obtaining 25 comments. . .")

    for comment in reddit.subreddit("dogs").comments(limit=25):
        if "dog" in comment.body and comment.id not in comments_replied_to and comment.author != reddit.user.me():
            print("String with \"dog\" found in comment " + comment.id)

            comment_reply = "You requested a Chuck Norris joke! Here it is:\n\n"

            joke = requests.get("https://api.chucknorris.io/jokes/random").json()["value"]

            comment_reply += ">" + joke

            comment_reply += "\n\nThis joke came from [ICNDB.com](http://icndb.com)."
            comment.reply(comment_reply)
            print("Replied to comment " + comment.id)

            comments_replied_to.append(comment.id)
            # Insert into the database
            conn = sqlite3.connect("comments_replied_to.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO replied_comments (comment_id) VALUES (?)", (comment.id,))
            conn.commit()
            conn.close()
    
    print("Sleeping for 10 seconds. . .")
    time.sleep(10)


def get_saved_comments():
    conn = sqlite3.connect("comments_replied_to.db")
    cursor = conn.cursor()
    cursor.execute("SELECT comment_id FROM replied_comments")
    comments_replied_to = [row[0] for row in cursor.fetchall()]
    conn.close()
    return comments_replied_to


def main():
    init_db()
    reddit = authenticate()
    comments_replied_to = get_saved_comments()
    while True:
        run_bot(reddit, comments_replied_to)


def init_db():
    conn = sqlite3.connect("comments_replied_to.db")
    cursor = conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS replied_comments (
                   comment_id TEXT PRIMARY KEY
                   )
    """)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()


# test commits