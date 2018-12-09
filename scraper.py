import urllib2
import ssl
import hashlib
import sys
import os
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
from dateutil.parser import parse

# This is a simple script that will scrape the resque failure pages and store that info in
# elasticsearch

BASE_URL  = 'https://services.carecloud.com'
BASE_PAGE = BASE_URL + '/resque/failed'
ELASTICSEARCH_HOSTS = ['https://search-marcos-test-ryuxkubedpfwdvbon4bnfsa2l4.us-east-1.es.amazonaws.com']
INDEX_NAME = 'resque-errors'
HOUR_OFFSET = 4 #Offset because resque is off by 4 hours, TODO: FIX

es = Elasticsearch(ELASTICSEARCH_HOSTS)

print "Starting script with values:"
print "*"*50
print "BASE_URL: %s" % BASE_URL
print "BASE_PAGE: %s" % BASE_PAGE
print "ELASTICSEARCH_HOSTS: %s" % ELASTICSEARCH_HOSTS
print "INDEX_NAME: %s" % INDEX_NAME
print "="*50

last_id = None
last_document = es.search(index=INDEX_NAME, size=1, sort='created_at:desc')

try:
    last_id = last_document['hits']['hits'][0]['_id']
    print "Last document found in index is " + last_id
except KeyError, e:
    print "No previous documents found in index: " + INDEX_NAME

print "Scraping pages..."

def scrape_error_info(container):
    hash = {}
    date = parse(container.span.text) + timedelta(hours=HOUR_OFFSET)
    date = date.strftime('%Y-%m-%dT%H:%M:%SZ') # Use a format ES can understand
    hash['worker'] = container.a.text.split(':')[0]
    hash['port'] = container.a.text.split(':')[1]
    hash['stacktrace'] = container.find_all('pre')[1].text
    hash['class'] = container.code.text
    hash['created_at'] = date #container.span.text
    # hash['arguments'] = container.find_all('dd')[2].text #Uncomment once we can store PHI
    hash['exception'] = container.find_all('dd')[3].text
    hash['id'] = hashlib.md5("s"+hash['class']+hash['created_at']).hexdigest()
    return hash


target_page = BASE_PAGE
context = ssl._create_unverified_context()

while True:
    print "Scraping " + target_page
    current_page = urllib2.urlopen(target_page, context=context)
    doc = BeautifulSoup(current_page, 'html.parser')
    failed_container = doc.find('ul', class_="failed")
    error_containers = failed_container.find_all('li')

    for container in error_containers:
        hash = scrape_error_info(container)
        if last_id == hash['id']:
            print "="*50
            print "last id " + last_id + " found. Exiting."
            sys.exit()
        res = es.index(index=INDEX_NAME, doc_type='error', id=hash['id'], body=hash)
        print res
        print "__________"

    if doc.find('a', class_="more"):
        target_page = BASE_URL + doc.find('a', class_="more")['href']
    else:
        break

