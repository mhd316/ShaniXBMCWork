# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcplugin
import urllib2,urllib,cgi, re
import HTMLParser
import xbmcaddon
import json
import traceback
import os
import cookielib
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, BeautifulSOAP
import datetime
import time
import sys
import CustomPlayer

try:    
	import StorageServer
except:
	print 'using dummy storage'
	import storageserverdummy as StorageServer

__addon__       = xbmcaddon.Addon()
__addonname__   = __addon__.getAddonInfo('name')
__icon__        = __addon__.getAddonInfo('icon')
addon_id = 'plugin.video.shahidmbcnet'
selfAddon = xbmcaddon.Addon(id=addon_id)
addonPath = xbmcaddon.Addon().getAddonInfo("path")
addonArt = os.path.join(addonPath,'resources/images')
#communityStreamPath = os.path.join(addonPath,'resources/community')
communityStreamPath = os.path.join(addonPath,'resources')
communityStreamPath =os.path.join(communityStreamPath,'community')

COOKIEFILE = communityStreamPath+'/teletdunetPlayerLoginCookie.lwp'
cache_table         = 'ShahidArabic'
cache2Hr              = StorageServer.StorageServer(cache_table,1)

teledunet_htmlfile='TeledunetchannelList.html'
profile_path =  xbmc.translatePath(selfAddon.getAddonInfo('profile'))
def PlayStream(sourceEtree, urlSoup, name, url):
    try:
        channelId = urlSoup.url.text
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('XBMC', 'Communicating with Teledunet')
        pDialog.update(10, 'fetching channel page')
        loginName=selfAddon.getSetting( "teledunetTvLogin" )

        howMaytimes=2    
        totalTried=0
        doDummy=False           
        while totalTried<howMaytimes:
            totalTried+=1
            if 1==1:
                newURL='http://www.teledunet.com/mobile/'
                print 'newURL',newURL
                token=''
                try:
                    link=None
                    result = getChannelHTML(channelId);#cache2Hr.cacheFunction(getChannelHTML)
                    
                    if result:
                        link=result['link']
                        token=result['token']
                        mainpage=result['mainpage']
                        
                        print 'file_exists',len(link)
                    else:
                        print 'cache or the url failed!!'
                    rtmp =re.findall(('rtmp://(.*?)/%s\''%channelId), link)
                    if len(rtmp)==0:
                        print 'creating it manually'
                        rtmp='rtmp://127.0.0.1:1935/live/%s'%channelId
                    else:
                        rtmp=rtmp[0]               
                    print 'rtmp1',rtmp
                    rtmp='rtmp://%s/%s'%(rtmp,channelId)
                    print 'rtmp2',rtmp
                    if '127.0.0.1' in rtmp:
                        server_pat='Array\((.*?)\);'
                        servers_array=re.findall(server_pat, link)[0].replace('\'','')+','
                        print servers_array
                        server_pat="(rtmp:.*?),"
                        servers_array=re.findall(server_pat, servers_array)
                        rtmp=servers_array[0] 
                except:
                    clearFileCache()            
                    traceback.print_exc(file=sys.stdout)
                    print 'trying backup'
                    try:
                        link=getUrl("http://pastebin.com/raw.php?i=z66yHXcG", getCookieJar())
                        rtmp =re.findall(('rtmp://(.*?)/%s\''%channelId), link)[0]
                        rtmp='rtmp://%s/%s'%(rtmp,channelId)
                    except:
                        traceback.print_exc(file=sys.stdout)
                        rtmp='rtmp://5.196.84.28:1935/live/%s'%(channelId)
                        print 'error in channel using hardcoded value'
            pDialog.update(80, 'trying to play')
            liveLink= sourceEtree.findtext('rtmpstring');
            freeCH='2m'
            ip_patt="ip='(.*?)';"
            dz_patt="dz='(.*?)';"
            today = datetime.datetime.now()
            v1 = 234*(366-(today - datetime.datetime(today.year, 1, 1)).days + 0);
            v2 = 222; #something wrong in calc, may be timezone?
            dz=re.findall(dz_patt, link)[0]        
            ip=re.findall(ip_patt, link)[0]
            ip2=''.join(ip.split('.')[0:4])
            print 'dz',	dz        
            access_id=str(((365-int(dz))*long(ip2)*v1)+v2)
            access_id='?id1='+access_id
            access_iddummy='?id1=1'

       
            liveLinkdummy=liveLink%(rtmp,'',access_id,freeCH,selfAddon.getSetting( "teledunetTvLogin" ),'')
            liveLink=liveLink%(rtmp,channelId,access_id,freeCH,selfAddon.getSetting( "teledunetTvLogin" ),token)

                    
            name+='-Teledunet'
            print 'liveLink',liveLink
            pDialog.close()
#            try:
#                howMaytimes=int(selfAddon.getSetting( "teledunetRetryCount" ))
#            except:pass

            pDialog = xbmcgui.DialogProgress()
            pDialog.create('XBMC', 'Playing channel')

            patt='add_friend=(.*?)\'.*?<img src="premium.png"'
            res=re.findall(patt, mainpage)
            randomuser=''
            if res and len(res)>0:
                randomuser=res[0]
      
#		howMaytimes=2
#		totalTried=0        
#		while totalTried<howMaytimes:
            if 1==1:##instead of while
                liveLinkPlay=liveLink
                if totalTried==1 and doDummy:
                    liveLinkPlay=liveLinkdummy
                pDialog.update((totalTried*100)/howMaytimes, 'Teledunet: Try #' + str(totalTried) +' of ' + str(howMaytimes))
                listitem = xbmcgui.ListItem( label = str(name), iconImage = "DefaultVideo.png", thumbnailImage = xbmc.getInfoImage( "ListItem.Thumb" ), path=liveLinkPlay )
                player = CustomPlayer.MyXBMCPlayer()
                #xbmc.Player().play( liveLink,listitem)
                start = time.time()  
                player.pdialogue=pDialog
                if pDialog.iscanceled():
                    break
                if 1==2 and totalTried==2:
                    if len(randomuser)==0:
                        break
                    else:
                        liveLinkPlay=re.sub('user=(.*?)&','user=%s&'%randomuser,liveLinkPlay)
                player.play( liveLinkPlay,listitem)  
                if pDialog.iscanceled():
                    break
                #pDialog.close()
                while player.is_active:
                    xbmc.sleep(200)
                #return player.urlplayed
                done = time.time()
                elapsed = done - start
                #save file
                if player.urlplayed and elapsed>=3:
                    return True
        pDialog.close()
        return False
    except:
        traceback.print_exc(file=sys.stdout)    
    return False  



def getCookieJarOld(login=False):
	try:
		cookieJar=None
		COOKIEFILE = communityStreamPath+'/teletdunetPlayerLoginCookie.lwp'
		try:
			cookieJar = cookielib.LWPCookieJar()
			cookieJar.load(COOKIEFILE)
		except:
			traceback.print_exc(file=sys.stdout)	
			cookieJar=None
		loginPerformed=False
		if login or not cookieJar==None:
			cookieJar=performLogin()
			loginPerformed=True
		if cookieJar:
			cookieJar.save (COOKIEFILE)
		print 'saved'
		return cookieJar,loginPerformed
	except:
		traceback.print_exc(file=sys.stdout)
		return None, False
	
def performLoginOLD():
	print 'performing login'
	userName=selfAddon.getSetting( "teledunetTvLogin" )
	password=selfAddon.getSetting( "teledunetTvPassword" )
	cookieJar = cookielib.LWPCookieJar()
	cookie_handler = urllib2.HTTPCookieProcessor(cookieJar)
	opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
	opener = urllib2.install_opener(opener)
	req = urllib2.Request('http://www.teledunet.com/boutique/connexion.php')
	req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
	post={'login_user':userName,'pass_user':password}
	post = urllib.urlencode(post)
	response = urllib2.urlopen(req,post)
	link=response.read()
	response.close()
	now_datetime=datetime.datetime.now()
	req = urllib2.Request('http://www.teledunet.com/')#access main page too
	req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return cookieJar;

def performLogin():
	try:
		cookieJar=cookielib.LWPCookieJar()
		userName=selfAddon.getSetting( "teledunetTvLogin" )
		password=selfAddon.getSetting( "teledunetTvPassword" )
		print 'Values are ',userName,password
		post={'login_user':userName,'pass_user':password}
		post = urllib.urlencode(post)
		html_text=getUrl("http://www.teledunet.com/boutique/connexion.php",cookieJar,post)
		cookieJar.save (COOKIEFILE,ignore_discard=True)
		#print 'cookie jar saved',cookieJar
		#html_text=getUrl("http://www.teledunet.com/",cookieJar,referer='http://www.teledunet.com/boutique/connexion.php')
		#cookieJar.save (COOKIEFILE,ignore_discard=True)
		return shouldforceLogin(cookieJar)==False
	except:
		traceback.print_exc(file=sys.stdout)
		return False


def shoudforceLoginOLD():
    return True #disable login
    try:
#        import dateime
        lastUpdate=selfAddon.getSetting( "lastteledunetLogin" )
        print 'lastUpdate',lastUpdate
        do_login=False
        now_datetime=datetime.datetime.now()
        if lastUpdate==None or lastUpdate=="":
            do_login=True
        else:
            print 'lastlogin',lastUpdate
            try:
                lastUpdate=datetime.datetime.strptime(lastUpdate,"%Y-%m-%d %H:%M:%S")
            except TypeError:
                lastUpdate = datetime.datetime.fromtimestamp(time.mktime(time.strptime(lastUpdate, "%Y-%m-%d %H:%M:%S")))
        
            t=(now_datetime-lastUpdate).seconds/60
            print 'lastUpdate',lastUpdate,now_datetime
            print 't',t
            if t>15:
                do_login=True
        print 'do_login',do_login
        return do_login
    except:
        traceback.print_exc(file=sys.stdout)
    return True

def clearFileCache():
	cache2Hr.delete('%')
	
def storeInFile(text_to_store,FileName):
	try:
		File_name=os.path.join(profile_path,FileName )
		localFile = open(File_name, "wb")
		localFile.write(text_to_store)
		localFile.close()
		return True
	except:
		traceback.print_exc(file=sys.stdout)
	return False

def getStoredFile(FileName):
	ret_value=None
	File_name=os.path.join(profile_path,FileName )
	try:
		data = open(File_name, "r").read()
		ret_value=data
	except:
		traceback.print_exc(file=sys.stdout)
	return ret_value
	
def getCookieJar():
	cookieJar=None

	try:
		cookieJar = cookielib.LWPCookieJar()
		cookieJar.load(COOKIEFILE,ignore_discard=True)
	except: 
		cookieJar=None
	
	if not cookieJar:
		cookieJar = cookielib.LWPCookieJar()

	return cookieJar

def getUrl(url, cookieJar=None,post=None,referer=None):

	cookie_handler = urllib2.HTTPCookieProcessor(cookieJar)
	opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
	#opener = urllib2.install_opener(opener)
	req = urllib2.Request(url)
	req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
	if referer:
		req.add_header('Referer',referer)
	response = opener.open(req,post,timeout=30)
	link=response.read()
	response.close()
	return link;
	
def shouldforceLogin(cookieJar=None):
    try:
        url="http://www.teledunet.com/boutique/connexion.php"
        if not cookieJar:
            cookieJar=getCookieJar()
        html_txt=getUrl(url,cookieJar)
        
            
        if '<input name="login_user"' in html_txt:
            return True
        else:
            return False
    except:
        traceback.print_exc(file=sys.stdout)
    return True

def getChannelHTML(cid):
    try:
        cookie_jar=None
        print 'Getting HTML from Teledunet'
        loginName=selfAddon.getSetting( "teledunetTvLogin" )
        if not loginName=="":
            if shouldforceLogin():
                if performLogin():
                    print 'done login'
                else:
                    print 'login failed??'
            else:
                print 'Login not forced.. perhaps reusing the session'
            cookie_jar=getCookieJar()
        else:
            cookie_jar=cookielib.LWPCookieJar()
        getUrl('http://www.teledunet.com/', cookie_jar)
        mainpage=getUrl('http://www.teledunet.com/', cookie_jar,referer='http://www.teledunet.com/boutique/connexion.php')
 
        import time
        #currentTime=int(time.time()*1000)
        
        rnd=time.time()*1000
        post={'rndval':rnd}
        post = urllib.urlencode(post)
        html=getUrl('http://www.teledunet.com/comment.php?w=100%&pseudo_2=&get_comments=Salon_Publique', cookie_jar,referer='http://www.teledunet.com/',post=post)
        answer=re.findall('answer\',\'(.*?)\'', html)
        newod1=None
        if answer and len(answer)>0:
            for ans in answer:
                if not newod1: 
                    rnd=time.time()*1000
                    post={'answer':ans,'rndval':rnd}
                    spacerUrl="http://www.teledunet.com/spacer.php"
                    post = urllib.urlencode(post)
                    html=getUrl(spacerUrl,cookie_jar ,post,'http://www.teledunet.com/')
                    if 'id1' in html:
                        newod1=re.findall('id1=(.*)', html)[0]
        if newod1==None:
            post={'onData':'[type Function]','secure':'1'}
            post = urllib.urlencode(post)#Referer: http://www.teledunet.com/player.swf?
            html=getUrl('http://www.teledunet.com/security.php',cookie_jar ,post,'http://www.teledunet.com/player.swf?')        
            if 'id1' in html:
                newod1=re.findall('id1=(.*)', html)[0]
        token=''
        import random
        token=str(   int('11' +  str(int(999999 +random.random() * (99999999 - 999999)))) * 3353);
        
#        post=None
#        testUrl='http://www.teledunet.com/mobile//player.swf?id0=%s&channel=abu_dhabi_drama&user=&token=%s'%(newod1,token) 
#        getUrl(testUrl,cookie_jar ,post,'http://www.teledunet.com/mobile/') 

        newURL='http://www.teledunet.com/mobile/'
        link=getUrl(newURL,cookie_jar ,None,'http://www.teledunet.com/')
        post={'rndval':rnd}
        post = urllib.urlencode(post)
        link=getUrl(newURL,cookie_jar ,post,'http://www.teledunet.com/')
        link=getUrl(newURL,cookie_jar ,None,'http://www.teledunet.com/')

        if newod1:
            link+='fromspacer('+newod1+")"
        
        return {'link':link,'token':token,'mainpage':mainpage}
    except:
        traceback.print_exc(file=sys.stdout)
        return ''
