# -*- coding: utf-8 -*-
#
#     Copyright (C) 2018 zinobg@gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import re,os,urllib2,urllib
import xbmcplugin,xbmcgui,xbmcaddon
import weblogin

# Getting username and password from addon settings
addon=xbmcaddon.Addon()
username=addon.getSetting('username')
password=addon.getSetting('password')
videoquality=addon.getSetting('highvideoquality')

BASE='https://neterra.tv/'
header_string='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
url_login=BASE+'sign-in'
url_live=BASE+'live'
url_videos=BASE+'videos'

def LIST_CHANNELS():
    channel_source=weblogin.doLogin('',username,password,url_login)
    channel_source=weblogin.openUrl(url_live)
    match=re.compile('<a href="(.+?)".*\n.*\n.*\n.*>(.+?)<\/span>.*\n.*<img src="(.+?)"').findall(channel_source)
    for url_chann,name,thumbnail in match:
        if (videoquality=="true"):
            url_chann=url_chann+"?quality=25&type=html"
        addDir(name,url_chann,1,thumbnail)

def LIST_VID():
    channel_source=weblogin.doLogin('',username,password,url_login)
    channel_source=weblogin.openUrl(url_videos)
    match=re.compile('<li>\s*.*<a href="(.+?)"\s*class="side-nav__item.*"\s*>(.+?)<\/a>').findall(channel_source)
    for url_chann,name in match:
        addDir(name,url_chann,2,'')

def INDEX_VID(name,url):
    channel_source=weblogin.doLogin('',username,password,url_login)
    channel_source=weblogin.openUrl(url)
    match=re.compile(',{"id":(.+?),"tag":"(.+?)","name":"(.+?)"').findall(channel_source)
    for id,url,name in match:
        url=url_videos+"/"+url
        try:
            name=name.decode('unicode-escape').encode('utf-8')
        except:
            pass
        addDir(name,url,3,'')

def INDEX_VID_CAT(name,url):
    channel_source=weblogin.openUrl(url)
    match=re.compile('<a href="(.+?)".*\n.*class="playlist-item".*\n.*\n.*<div class="playlist-item__title">.*\n.*<p>(.+?)<\/p>').findall(channel_source)
    for url,name in match:
        if (videoquality=="true"):
            url=url+"?quality=25&type=html"
        addDir(name,url,4,'')

def INDEX_VID_STREAM(name,url):
    channel_source=weblogin.openUrl(url)
    match=re.compile(',"link":"(.+?)","formats"').findall(channel_source)
    stream = match[0].replace("\/","/")
    if 'rtmps' in stream:
        xbmcgui.Dialog().notification('Switch to HTML 5 player','Switch to HTML 5 player',xbmcgui.NOTIFICATION_ERROR,8000,sound=True)
        raise SystemExit
    addLink('PLAY: '+name,stream,'')
        
    
def INDEX_CHANNELS(name,url):
    channel_source=weblogin.doLogin('',username,password,url_login)
    channel_source=weblogin.openUrl(url)
    match=re.compile('"link":"(.+?)","formats').findall(channel_source)
    stream = match[0].replace("\/","/")
    if 'rtmps' in stream:
        xbmcgui.Dialog().notification('Switch to HTML 5 player','Switch to HTML 5 player',xbmcgui.NOTIFICATION_ERROR,8000,sound=True)
        raise SystemExit
    addLink('PLAY: '+name,stream,'')
    
def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                 param[splitparams[0]]=splitparams[1]
    return param

def addLink(name,url,iconimage):
    ok=True
    liz=xbmcgui.ListItem(name,iconImage="DefaultVideo.png",thumbnailImage=iconimage)
    liz.setInfo(type="Video",infoLabels={"Title":name})
    liz.setProperty('IsPlayable','true')
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    return ok

def addDir(name,url,mode,iconimage):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    ok=True
    liz=xbmcgui.ListItem(name,iconImage="DefaultFolder.png",thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={ "Title": name })
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

params=get_params()
url=None
name=None
mode=None

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass

xbmc.log("Mode: "+str(mode))
xbmc.log("URL: "+str(url))
xbmc.log("Name: "+str(name))

if mode==None or url==None or len(url)<1:
    dialog=xbmcgui.Dialog()
    ret=dialog.select('',['ГЛЕДАЙ','ВИДЕОТЕКА'])
    if(ret==0):
        LIST_CHANNELS()
    elif(ret==1):
        LIST_VID()

elif mode==1:
    INDEX_CHANNELS(name,url)

elif mode==2:
    INDEX_VID(name,url)

elif mode==3:
    INDEX_VID_CAT(name,url)

elif mode==4:
    INDEX_VID_STREAM(name,url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))