import os
import sys
import unittest

sys.path.insert(0, os.path.abspath('..'))
import webpoll

hackernews_html = "hackernews_test.html"


class WebPollTest(unittest.TestCase):

    def test_filter_links(self):
        with open(hackernews_html, "r") as f:
            html_page = "".join(f.readlines())
        links = webpoll.filter_links(html_page)
        self.assertEquals(227, len(links))
        self.assertIn(
            "https://icomp.de/shop-icomp/en/33/items/commodore-back-in-germany.html", links)

    def test_msg_builder(self):
        notifications = [webpoll.Notification(url, link) for (url, link) in [
            ("a", "b"), ("c", "d")]]
        msg_body = webpoll.msg_body_builder(notifications, "now")

        expected_body = """Hello, as of now

The web page a links to b.
The web page c links to d. 

Chur,
Webpoll
"""
        self.assertEquals(expected_body, msg_body)
        self.assertRaises(AssertionError, webpoll.msg_body_builder,  [], "now")
