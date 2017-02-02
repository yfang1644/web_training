#!/usr/bin/env python
# encoding: utf-8
# File Name: parse_link.py
# Author: Fang Yuan (yfang@nju.edu.cn)
# Created Time: Thu 02 Feb 2017 10:07:26 AM CST

from HTMLParser import HTMLParser
from cStringIO import StringIO
from urllib2 import urlopen
from urlparse import urljoin
from bs4 import BeautifulSoup, SoupStrainer

from html5lib import parse, treebuilders

URLs = ('http://www.iqiyi.com', 'http://python.org',)


def output(x):
    print '\n'.join(sorted(set(x)))


def simpleBS(url, f):
    'simpleBS'
    parsed = BeautifulSoup(f)
    tags = parsed.findAll('a')
    links = [urljoin(url, tag['href']) for tag in tags]
    output(links)


def fasterBS(url, f):
    'fasterBS'
    output(urljoin(url, x['href']) for x in BeautifulSoup(
        f, parse_only=SoupStrainer('a')))


def htmlparser(url, f):
    class AnchorParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag != 'a':
                return
            if not hasattr(self, 'data'):
                self.data = []
            for attr in attrs:
                if attr[0] == 'href':
                    self.data.append(attr[1])
    parser = AnchorParser()
    parser.feed(f.read())
    output(urljoin(url, x) for x in parser.data)


def html5libparse(url, f):
    'html5lib'
    output(urljoin(url, x.attributes['href'])
           for x in parse(f) if isinstance(x,
           treebuilders.simpletree.Element) and
           x.name == 'a')


def process(url, data):
    print '\n*** Simple BS'
    data.seek(0)
#    simpleBS(url, data)
    print '\n*** faster BS'
    data.seek(0)
#    fasterBS(url, data)
    print '\n*** HTMLParser'
    data.seek(0)
    htmlparser(url, data)
    print '\n*** HTML5lib'
    data.seek(0)
    html5libparse(url, data)


def main():
    for url in URLs:
        f = urlopen(url)
        data = StringIO(f.read())
        f.close()
        process(url, data)

if __name__ == '__main__':
    main()
