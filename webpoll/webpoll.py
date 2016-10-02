import urllib2
from bs4 import BeautifulSoup
import re
import time
import threading
import datetime
import smtplib
import os
import ConfigParser
import collections
import getpass
import logging
import logging.handlers
import sys

Notification = collections.namedtuple("Notification", ["url", "link"])
logger = logging.getLogger("webpoll")

def fetch(url):
    """make an HTTP GET request and return the data @ url"""
    try:
        req = urllib2.Request(url)
        return urllib2.urlopen(req).read()
    except Exception as ex:
        logger.error("Failed to fetch url "+ url +" due to "+str(ex))
        return None

def filter_links(html_page):
    """
    args: 
        page: a str formatted like an html  document
    return: equivalent to x-parth //a[@href]
    """
    soup = BeautifulSoup(html_page, "html.parser")
    return [link.get("href") for link in soup.find_all("a")]


def msg_body_builder(notifications, timestamp):
    """
    args:
        notifications: a list of Notification tuples
        timestamp: a string timestamp
    return:
        email body expressing notification information
    """
    assert(len(notifications) > 0)

    notification_msg = "\n".join(["The web page {} links to {}.".format(n.url, n.link)
                                  for n in notifications])

    return """Hello, as of {}

{} 

Chur,
Webpoll
""".format(timestamp, notification_msg)


class WebPoll(object):

    def __init__(self, target_urls, target_links, poll_interval,
                 email_server_address, email_user, email_password, email_targets):
        """
        args: 
            target_urls: a list of urls to poll
            target_links: a list of url-fragments (or regexs) to look for
            poll_interval: time interval in seconds
            email_server_address: email server that will send messages
            email_user: credentials for email_server_address
            email_password: credentials for email_server_address
            email_targets: a list of email-recipients. When email_targets is None or empty
            defaults to [email_user]
        """
        self.target_urls = target_urls
        self.target_links = [re.compile(regex) for regex in target_links]
        self.poll_interval = poll_interval
        self.email_server_address = email_server_address
        self.email_user = email_user
        self.email_password = email_password
        self.email_targets = [
            email_user] if not email_targets else email_targets
        self.lock = threading.Lock()
        self._is_finished = False

    @property
    def is_finished(self):
        with self.lock:
            return self._is_finished

    @is_finished.setter
    def is_finished(self, is_finished):
        with self.lock:
            self._is_finished = is_finished

    def close(self):
        self.is_finished = True

    def tick(self, now):
        """
        fetches and filters the links in each page in self.target_urls 
        and notifies each of self.email_targets 
        via email if any of the links match any of self.target_links
        """
        pages = [fetch(url) for url in self.target_urls]

        notifications = [Notification(url, link)
                         for regex in self.target_links
                         for page in pages
                         for link in filter_links(page)
                         if page is not None
                         if regex.search(link)]

        if notifications:
            email_body = msg_body_builder(notifications, now.isoformat())
            logger.debug("Sending email message")
            self.notify_by_email(email_body)

    def notify_by_email(self, msg_body):
        """
        send email message from self.email_user to self.email_targets stating that link_regex_pattern is
        in url as of timestamp
        """
        server = smtplib.SMTP(self.email_server_address)
        server.starttls()
        server.login(self.email_user, self.email_password)
        for email_target in self.email_targets:
            server.sendmail(self.email_user, email_target, msg_body)
        server.quit()

    def run(self):
        while not self.is_finished:
            try:
                start_time = datetime.datetime.now()
                self.tick(start_time)
                end_time = datetime.datetime.now()
            except Exception as ex:
                logger.error("Tick failed! :"+str(ex))
            finally:
                time_delta = end_time - start_time
                sleep_seconds = max(0, self.poll_interval - time_delta.seconds)
                time.sleep(sleep_seconds)


def main():
    config = ConfigParser.ConfigParser()
    config.read(["app.cfg", os.path.expanduser("~/.webpoll.cfg")])
    
    def get_param(param, default=None):
        try:
            return config.get("webpoll", param)
        except ConfigParser.NoOptionError:
            return default
        
    log_path = get_param("log_path", os.path.expanduser("~/.webpoll.log"))
    log_format = logging.Formatter(fmt='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    log_handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=1024*1024, backupCount=5)
    log_handler.setFormatter(log_format)
    logger.addHandler(log_handler)
    logger.setLevel(logging.DEBUG)

    email_user = get_param("email_user")
    assert(email_user)
    
    get_list_param = lambda x: get_param(x).split(",")

    email_password = get_param("email_password")
    if not email_password:
        email_password = getpass.getpass("Enter email password for: '{}' : ".format(email_user))

    webpoll = WebPoll(
        get_list_param("links"),
        get_list_param("link_regexs"),
        int(get_param("poll_interval_seconds", "600")),
        get_param("email_server_address", "smtp.gmail.com:587"),
        email_user,
        email_password,
        get_param("email_targets"))

    webpoll.run()

if __name__ == "__main__":
    main()
    poll_interval_seconds=6
