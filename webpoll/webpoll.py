import urllib2
from bs4 import BeautifulSoup
import re
import time
import threading
import datetime
import smtplib
import os, ConfigParser

def fetch(url):
    """make an HTTP GET request and return the data @ url"""
    req = urllib2.Request(url)
    return urllib2.urlopen(req).read()

def filter_links(html_page):
    """
    args: 
        page: a str formatted like an html  document
    return: equivalent to x-parth //a[@href]
    """
    soup = BeautifulSoup(html_page, "html.parser")
    return [link.get("href") for link in soup.find_all("a")]

def msg_body_builder(url, link_regex_pattern, timestamp):
    return """Hello, 
The web-page located @ '{}', currently links to {} as of {}.

Chur,
Webpoll
""".format(url, link_regex_pattern, timestamp)


class WebPoll(object):
    def __init__(self, target_urls, target_links, poll_interval, 
            email_server_address, email_user, email_password, email_targets):
        """
        args: 
            target_urls: a list of urls to poll
            target_links: a list of url-fragments (or regexs) to look for
            email_server_address: email server that will send messages
            email_user: credentials for email_server_address
            email_password: credentials for email_server_address
            email_targets: a list of email-recipients
        """
        self.target_urls = target_urls
        self.target_links =  [re.compile(regex) for regex in target_links]
        self.poll_interval = poll_interval
        self.email_server_address = email_server_address
        self.email_user =  email_user
        self.email_password = email_password
        self.email_targets = email_targets
        self.lock = threading.Lock()
        self._is_finished = False

    @property
    def is_finished(self):
        with self.lock:
            return self._is_finished

    @is_finished.setter
    def is_finished(self, var):
        with self.lock:
            self._is_finished = var 

    def close(self):
        self.is_finished = True

    def tick(self, now):
        for url in self.target_urls:
            page = fetch(url)
            links = filter_links(page)
            for link in links: 
                for target_link in self.target_links:
                    if target_link.search(link):
                        self.notify_by_email(url, target_link, now)

    def notify_by_email(self, url, link_regex_pattern, timestamp):
        """
        send email message from self.email_user to self.email_targets stating that link_regex_pattern is
        in url as of timestamp
        """
        email_body = msg_body_builder(url, link_regex_pattern, str(timestamp))

        server = smtplib.SMTP(self.email_server_address)
        server.login(self.email_user, self.email_password)
        for email_target in self.email_targets:
            server.sendmail(self.email_user, email_target, email_body)
        server.quit()

    def run(self):
        last_tick = None
        while not self.is_finished:
            start_time = datetime.datetime.now()
            self.tick(start_time)
            end_time = datetime.datetime.now()
            time_delta = end_time - start_time
            sleep_seconds = min(0, self.poll_interval - time_delta.seconds)
            time.sleep(sleep_seconds)

def main():
    config = ConfigParser.ConfigParser()
    config.read(["app.cfg", os.path.expanduser("~/.webpoll.cfg")])
    get_param = lambda x, default: config.get("webpoll", x, default)
    get_list_param = lambda x: get_param(x, None).split(",") 

    webpoll = WebPoll(
        get_list_param("links"),
        get_list_param("link_regexs"),
        get_param("poll_interval", 60*30),
        get_param("email_server_address", "smtp.gmail.com:587"),
        get_param("email_user", None),
        get_param("email_password", None),
        get_param("email_targets", None))

    webpoll.run()

if __name__ == "__main__":
    main()
