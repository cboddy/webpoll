import os
from setuptools import setup

setup(
        name="webpoll",
        version="0.0.1",
        author="Chris Boddy",
        author_email="chris@boddy.im",
        description="A utility to periodically fetch a set of web-pages, and send email notifications in the case that the content matches one or more specified regexs",
        license="Apache",
        keywords="html poll regex",
        packages=["webpoll"],
        entry_points = {
            "console_scripts": ["webpoll_daemon=webpoll.webpoll:main"]
            }
        )
