# -*- coding: utf-8 -*-
import os,re,urllib,urllib2
import xbmc, xbmcgui
import cookielib

header_string='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'

def check_login(source_login,username):
    logged_in_string=username
    if re.search(logged_in_string,source_login,re.IGNORECASE):
        return True
    else:
        return False
		
def openUrl(url):
    req=urllib2.Request(url)
    req.add_header('User-Agent',header_string)
    response=urllib2.urlopen(req)
    source=response.read()
    response.close()
    return source
	
def doLogin(cookiepath,username,password,url_to_open):
    #check if user has supplied only a folder path, or a full path
    if not os.path.isfile(cookiepath):
        #if the user supplied only a folder path, append on to the end of the path a filename.
        cookiepath=os.path.join(cookiepath,os.path.join(xbmc.translatePath('special://temp'),'cookies_neterratv.r1.lwp'))
    #delete any old version of the cookie file
    try:
        os.remove(cookiepath)
    except:
        pass

    if username and password:
        login_url=url_to_open
        cj = cookielib.LWPCookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)
        #get the CSRF token
        regexCSRF = r"CSRF_TOKEN\":\"(.*)\",\""
        req = urllib2.Request(login_url)
        req.add_header('User-Agent', header_string)
        response = opener.open(req)
        html = response.read()
        response.close()
        matches = re.finditer(regexCSRF, html, re.MULTILINE)
        for matchNum, match in list(enumerate(matches)):
            matchNum = matchNum + 1
            CSRF_TOKEN=match.group(1)
        #token gotten
        req=urllib2.Request(login_url)
        req.add_data('_token='+CSRF_TOKEN+'&username='+username+'&password='+password)
        req.add_header('User-Agent',header_string)
        response=opener.open(req)
        source_login=response.read()
        response.close()
        login=check_login(source_login,username)
        if login==True:
            cj.save(cookiepath)
            return source_login
        else:
            xbmcgui.Dialog().notification('[ Login ERROR ]','Wrong username or password!',xbmcgui.NOTIFICATION_ERROR,8000,sound=True)
            raise SystemExit
