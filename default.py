# -*- coding: utf-8 -*-

#v1.0.0 2009/11/08 by robinttt, initial release
#v1.1.0 2011/12/04 by d744000, full web scraping, added search.

import urllib, urllib2, os, re, sys
import gzip, StringIO #playvideo
import hashlib, time
from bs4 import BeautifulSoup

try:
#if 'XBMC' in os.path.realpath('.'):
    import xbmc, xbmcplugin, xbmcgui, xbmcaddon
except:
    xbmc = None
    urlparams = []

UserAgent = 'Mozilla/5.0 (Windows NT 5.1; rv:8.0) Gecko/20100101 Firefox/8.0'
URL_BASE = 'http://yinyue.kuwo.cn'
MAX_TEST = 300
INDENT_STR = '    '
BANNER_FMT = '[COLOR FFDEB887]【%s】[/COLOR]'

#
# Web process engine
#
def getUrlTree(url, data=None):
    headers = {
        'User-Agent': UserAgent,
    }
    if data and not isinstance(data, str):
        # 2-item tuple or param dict, assume utf-8
        data = urllib.urlencode(data)
    req = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    if response.headers.get('content-encoding', None) == 'gzip':
        httpdata = gzip.GzipFile(fileobj=StringIO.StringIO(httpdata)).read()
    # BeautifulSoup handles encoding, thus skip transcoding here.

    tree = BeautifulSoup(httpdata, "html.parser")
    print tree
    return tree


def driller(tree, lCont):
    #global item
    global context_params
    if not isinstance(lCont, list):
        lCont = [lCont]
    for cont in lCont:
        result = None
        context_params = cont.get('context', {})
        items = tree.find_all(*cont['tag'])
        #print("to find:", cont)
        for item in items:
            #print('found')
            if cont.get('vect', None):
                try:
                    result = cont['vect'](item)
                except:
                    pass
            if result != 'DRILLER_NO_DEEPER':
                if cont.get('child', None):
                    driller(item, cont['child'])


def processWebPage(tagHandler):
    global tree
    url = params['url']
    post = params.get('urlpost', None)
    tree = getUrlTree(url, post)
    driller(tree, tagHandler)
    endDir()


#
# Keyboard for search
#
def processSearch(url):
    key = get_params(url).get('key', None)
    params['url'] = url
    params['indent'] = str(True)
    params['search_key'] = key
    processWebPage(searchList)

# Choose ChineseKeyboard if script.module.keyboard.chinese is installed.


#
# Media player
#
def get_content_by_tag(tree, tag):
    f = tree.find(tag)
    if f and f.contents:
        return f.contents[0].encode('utf-8')
    else:
        return ''

def PlayMusic():
    mids = params['url']
    if xbmc:
        playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        playlist.clear()
    mids = mids.split('/')
    for mid in mids:
        if mid == '':
            continue
        tree = getUrlTree('http://player.kuwo.cn/webmusic/st/getNewMuiseByRid?rid=MUSIC_'+mid)
        title = get_content_by_tag(tree, 'name')
        # kuwo has names like "song name(抢听版)", causing lyrics look up failure
        true_title = title.split('(')[0].rstrip()
        artist = get_content_by_tag(tree, 'artist')
        iconimage = get_content_by_tag(tree, 'artist_pic240')

        # prefer AAC or WMA, somehow it starts or loads faster than the mp3 link,
        # change AAC to the first download.  edit by runner6502@gamil.com
        path = get_content_by_tag(tree, 'aacpath')
        dl = get_content_by_tag(tree, 'aacdl')
        if not (path and dl):
            path = get_content_by_tag(tree, 'path')
            dl = get_content_by_tag(tree, 'wmadl')
            if not (path and dl):
                path = get_content_by_tag(tree, 'mp3path')
                dl = get_content_by_tag(tree, 'mp3dl')

        if path and dl:
            timestamp = ("%x" % int(time.time()))[:8]
            hashstr = hashlib.md5("kuwo_web@1906/resource/%s%s" % (path, timestamp)).hexdigest()
            url = 'http://%s/%s/%s/resource/%s' % (dl, hashstr, timestamp, path)
            if xbmc:
                listitem=xbmcgui.ListItem(title, iconImage=iconimage, thumbnailImage=iconimage)
                listitem.setInfo( type="Music", infoLabels={ "Title": true_title, "Artist": artist} )
                playlist.add(url, listitem)
            else:
                print('PlayMusic: %s - %s, %s' % (title, artist, url))
    if xbmc:
        xbmc.Player().play(playlist)

#
# Utilities
#
def addBanner(name):
    ''' Add a banner, a button without action, but to separate groups of other buttons. '''
    # Burlywood color
    if name:
        name = BANNER_FMT % name
        addDir(name, '', 'pass', '', folder=False)

#
# Kuwo tag handlers
#

def extractName(item):
    if not item:
        return ''
    name = ''
    span_name = item.find('span')
    if span_name:
        name = span_name.contents[0]
    elif item.has_attr('title'):
        name = item['title']
    elif item.contents:
        content = item.contents[0]
        if 'String' in str(type(content)):
            #BeautifulSoup NavigableString
            name = content
        else:
            try:
                name = content['title']
            except:
                pass
    return name.encode('utf-8')

def extractHref(item):
    if item and item.has_attr('href'):
        return item['href'].encode('utf-8')
    return ''

def extractImg(item):
    if item:
        for k in ['lazy_src', 'sr', 'src', 'init_src']:
            if item.has_attr(k):
                return item[k].encode('utf-8')
    return ''



# 分类
def addHotMusic(item):
    l = re.findall('"musiclist":(\[.+\]),"rids"', item.text)
    if l:
        l = eval(l[0])
        mids = "/".join([d['musicrid'] for d in l])
        disp_title = params.get('playall_title', '播放全部歌曲')
        iconimg = params.get('playall_icon', '')
        addDir(disp_title,mids, 'PlayMusic()', iconimg, folder = False)
        for d in l:
            title = d['name']
            artist = d['artist']
            mid = d['musicrid']
            iconimage = ''
            addLink(title,artist,mid,'PlayMusic()',iconimage)

def addHotMusicList(item):
    ''' playlist item '''
    url = extractHref(item.a)
    name = extractName(item.a)
    iconimg = extractImg(item.a.img)
    print url, item.p
    playall_title = '播放【%s】所含曲目' % name
    context = {'indent':str(True), 'playall_title':playall_title, 'playall_icon': iconimg}
    addDir(INDENT_STR + name, url, 'processWebPage(hotMusic)', iconimg, context=context)

def addHotList(item):
    ''' playlist item '''
    url = extractHref(item.a)
    name = extractName(item.a)
    iconimg = extractImg(item.a.img)
    playall_title = '播放【%s】所含曲目' % name
    context = {'indent':str(True), 'playall_title':playall_title, 'playall_icon': iconimg}
    addDir(INDENT_STR + name, url, 'processWebPage(hotMusicListPage)', iconimg, context=context)


def addH1Banner(item):
    addBanner(item.h1.text.encode('utf-8'))



# 标签

hotMusic = {'tag': ('script', {}),
            'vect': addHotMusic}
hotMusicList = {'tag': ('li', {}),
                'vect': addHotMusicList}
hotMusicListPage = {'tag': ('ul', {'class': 'list_dongtai clearfix'}),
                    'child': hotMusicList}
hotList = {'tag': ('li', {}),
           'vect': addHotList}
hotPage = {'tag': ('ul', {'class': 'list_dongtai clearfix'}),
           'vect': addH1Banner,
           'child': hotList}


#
# XBMC plugin
#
def addLink(title,artist,url,mode,iconimage='',total=0,video=False):
    if not xbmc:
        try:
            print('addLink(%s, %s, %s, %s, %s)' % (title,artist,url,mode,iconimage))
        except:
            print('addLink(title?, artist?, %s, %s, %s)' % (url,mode,iconimage))
    u = make_param({"url": url, "mode": mode})
    displayname = artist + ' - ' + title if artist else title
    displayname = INDENT_STR + displayname
    itemType = "Video" if video else "Music"
    if xbmc:
        item=xbmcgui.ListItem(displayname, iconImage=iconimage, thumbnailImage=iconimage)
        item.setInfo( type=itemType, infoLabels={ "Title":title, "Artist":artist } )
        return xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=False,totalItems=total)
    else:
        print(u)
        urlparams.append(u)

def addDir(name, url, mode, iconimage='DefaultFolder.png', context={}, plot='', folder=True, total=0):
    if url == '#@':
        url = params['url']
    elif url.startswith('/'):
        url = URL_BASE + url

#  print('(%s, %s, %s, %s)' % (name,str(url)[:MAX_TEST],iconimage,str(context)[:MAX_TEST]))

    param = {"url": url, "mode": mode}
    param.update(context)
    u = make_param(param)
    if xbmc:
        item=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        return xbmcplugin.addDirectoryItem(pluginhandle,url=u,listitem=item,isFolder=folder,totalItems=total)
    else:
        urlparams.append(u)


def endDir(cache=True):
    if xbmc:
        xbmcplugin.endOfDirectory(pluginhandle, cacheToDisc=True)

def get_params(params):
    param = {}
    if len(params) >= 2:
        cleanedparams = params.rsplit('?',1)
        if len(cleanedparams) == 2:
            cleanedparams = cleanedparams[1]
        else:
            cleanedparams = params.replace('?','')
        param = dict(urllib2.urlparse.parse_qsl(cleanedparams))
#    print(param)
    return param

def make_param(query, url = None):
    if url == None: url = sys.argv[0] if xbmc else ""
    param = "%s?%s" % (url, urllib.urlencode(query))
    return param

if xbmc:
    pluginhandle = int(sys.argv[1])
##    xbmcplugin.setContent(pluginhandle, 'musicvideos')
##    addon = xbmcaddon.Addon('plugin.audio.kuwobox')
##    pluginpath = addon.getAddonInfo('path')
else:
    pluginhandle = 1

params = {}

def main():
    global params
    params = get_params(sys.argv[2])
    mode = params.get("mode", None)
    if mode:
        exec(mode)
    else:
        # params['url'] = URL_BASE
        addDir('分类', 'http://www.iqiyi.com', 'processWebPage(hotPage)')
        endDir()

def test():
    # Unit Test without XBMC environment
    def UTP(urlparam):
        sys.argv = ['plugin://plugin.audio.kuwobox/', '-1', urlparam]
        main()

    def testMenu(urlparams, items = [], url = None):
        print('testMenu(url="%s", items=%s)\n' % (url, items))
        if url and isinstance(url, str):
            UTP(url)
        if items and not isinstance(items, list):
            items = [items]
        for x in items:
            url = urlparams[x]
            print('\n\n\n ******* TESTING %s\n' % url[:MAX_TEST])
            UTP(url)

    test_url = [
        make_param({"url": 'http://www.iqiyi.com', "mode": "processWebPage(hotPage)"}),
        ]

    if test_url:
        for urlparam in test_url:
            UTP(urlparam)
    else:
        testMenu(urlparams, [], '')


context_params = {}
if xbmc:
    main()
else:
    test()
