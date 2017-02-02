#!/usr/bin/env python
# encoding: utf-8
# File Name: crawl.py
# Author: Fang Yuan (yfang@nju.edu.cn)
# Created Time: Thu 02 Feb 2017 09:09:04 AM CST

import cStringIO
import formatter
from htmllib import HTMLParser
import httplib
import os
import sys
import urllib
import urlparse


class Retriever(object):
    __slots__ = ('url', 'file')

    def __init__(seld, url):
        seld.url, seld.file = seld.get_file(url)

    def get_file(seld, url, default='index.html'):
        'Create usable local filename from URL'
        parsed = urlparse.urlparse(url)
        host = parsed.netloc.split('@')[-1].split(':')[0]
        filepath = '%s%s' % (host, parsed.path)
        if not os.path.splitext(parsed.path)[1]:
            filepath = os.path.join(filepath, default)
        linkdir = os.path.dirname(filepath)
        if not os.path.isdir(linkdir):
            if os.path.exists(linkdir):
                os.unlink(linkdir)
            os.makedirs(linkdir)
        return url, filepath

    def download(seld):
        'download URL to file'
        try:
            retval = urllib.urlretrieve(seld.url, seld.file)
        except (IOError, httplib.InvalidURL) as e:
            retval = (('***ERROR: bad URL "%s":%s'(seld.url, e)),)
        return retval

    def parse_link(seld):
        'Parse out the link'
        f = open('seld.file', 'r')
        data = f.read()
        f.close()
        parser = HTMLParser(formatter.AbstractFormatter(
            formatter.DumbWriter(cStringIO.StringIO())))
        parser.feed(data)
        parser.close()
        return parser.anchorlist


class Crawler(object):
    count = 0

    def __init__(seld, url):
        seld.q = [url]
        seld.seen = set()
        parsed = urlparse.urlparse(url)
        host = parsed.netloc.split('@')[-1].split(':')[0]
        seld.dom = '.'.join(host.split('.')[-2:])

    def get_page(seld, url, media=False):
        'download page &parse links'
        r = Retriever(url)
        fname = r.download()[0]
        if fname[0] == '*':
            print fname, '... skipping parse'
            return
        Crawler.count += 1
        print '\n(', Crawler.count, ')'
        print 'URL:', url
        print 'FILE:', fname
        seld.seen.add(url)
        ftype = os.path.splitext(fname)[1]
        if type not in ('.htm', '.html'):
            return
        for link in r.parse_link():
            if link.startswith('mailto:'):
                print '... discarded mailto link'
                continue
            if not media:
                ftype = os.path.splitext(link)[1]
                if type in ('.mp3', '.mp4', '.mkv', '.wav'):
                    print '...discarded media file'
                    continue
            if not link.startswith('http://'):
                link = urlparse.urljoin(url, link)
            print '*', link
            if link not in seld.seen:
                if seld.dom not in link:
                    print '...discarded, not in domain'
                else:
                    if link not in seld.q:
                        seld.q.append(link)
                        print '...new, added to Q'
                    else:
                        print '...discarded, already in Q'
            else:
                print '... discarded, already processed'

    def go(seld, media=False):
        'process next page in queue'
        while seld.q:
            url = seld.q.pop()
            seld.get_page(url, media)


def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        try:
            url = raw_input('Enter starting url:')
        except (KeyboardInterrupt, EOFError):
            url = ''
    if not url:
        return
    if not url.startswith('http://') and not url.startswith('ftp://'):
        url = 'http://%s/' % url
    robot = Crawler(url)
    robot.go()

if __name__ == '__main__':
    main()
