#! /usr/bin/env python

"""Return the count of unread items. This can be used as a Python module
or a command-line script.

unread_count.main () returns the count."""

import urllib
import urllib2
import re
from lxml import etree

from account import *

def authenticate ():
    "Authenticate to obtain SID"
    auth_url = 'https://www.google.com/accounts/ClientLogin'
    auth_req_data = urllib.urlencode({'Email': username,
                                      'Passwd': password,
                                      'service': 'reader'})
    auth_req = urllib2.Request(auth_url, data=auth_req_data)
    auth_resp = urllib2.urlopen(auth_req)
    auth_resp_content = auth_resp.read()
    auth_resp_dict = dict(x.split('=') for x in auth_resp_content.split('\n') if x)
    auth_token = auth_resp_dict["Auth"]

    return auth_token

def get (auth_token):
    "Get XML data"
# Create a cookie in the header using the SID
    header = {}
    header['Authorization'] = 'GoogleLogin auth=%s' % auth_token

    reader_base_url = 'http://www.google.com/reader/api/0/unread-count?%s'
    reader_req_data = urllib.urlencode({'all': 'true',
                                        'output': 'xml'})
    reader_url = reader_base_url % (reader_req_data)
    reader_req = urllib2.Request(reader_url, None, header)
    reader_resp = urllib2.urlopen(reader_req)
    reader_resp_content = reader_resp.read()

    return reader_resp_content

def find_reading_list (string_node):
    return re.match (r'user/\d+/state/com.google/reading-list',
                     string_node.text)

def find_count (xml):
    "Find unread count"
    root = etree.fromstring (xml)

    ids = root.xpath ('/object/list[@name="unreadcounts"]/object/string[@name="id"]')

    node = filter (find_reading_list, ids)[0]

    node = node.xpath ('../number[@name="count"]')[0]

    return node.text

def main ():
    "Return count of unread items in Google Reader"
    auth_token = authenticate ()
    xml = get (auth_token)
    return int (find_count (xml))

if __name__ == "__main__":
    print main ()
