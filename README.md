# Webpoll
A python-2 utility to periodically fetch a set of web-pages, and send email notifications in the case that the content matches one or more specified regexs.

### Install
To install webpoll, install pip, use it to install the requirements and then run the setup script.

<pre> 
sudo apt-get install pip
pip install -r requirements.txt
sudo python setup.py install
</pre>

### Running
After installing the script webpoll_daemon should be available on your path variable. To run from anywhere do

> webpoll_daemon

### Config
The config file should be added to **~/.webpoll.cfg** and look something like this

<pre>
[webpoll]
links=
link_regexs=
email_user=
email_server_address=smtp.gmail.com:587
email_recipients=email_user
poll_interval_seconds=600
</pre>

where:

* links: csv links
* link_regexs: csv of regexs to search for in thelinks
* email_user: the account username from which notifications will be sent
* email_server: the smtp server that will send the messages (default shown)
* email_recipients: csv list of recipients that will recieve the notification messages (default shown)
* poll_interval_seconds: the time interval between sucessive crawls of each link
    
Running the daemon script will prompt for the password for email_user.


### Logging
A rotating log file stored at **~/.weboll.log**
