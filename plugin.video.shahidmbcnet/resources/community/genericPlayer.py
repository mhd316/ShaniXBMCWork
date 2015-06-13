# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcplugin
import urllib2,urllib,cgi, re
import HTMLParser
import xbmcaddon
import json
import traceback
import os
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, BeautifulSOAP
import time
import sys
import  CustomPlayer
import base64
import cookielib

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

class NoRedirection(urllib2.HTTPErrorProcessor):
   def http_response(self, request, response):
       return response
   https_response = http_response

def PlayStream(sourceEtree, urlSoup, name, url):
    try:
        #url = urlSoup.url.text
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('XBMC', 'Parsing the xml file')
        pDialog.update(10, 'fetching channel info')
        title=''
        link=''
        sc=''
        try:
            link=urlSoup.item.link.text
            sc=sourceEtree.findtext('sname')
            title=urlSoup.item.title.text
        except: pass
        if link=='':
            timeD = 2000  #in miliseconds
            line1="couldn't read title and link"
            xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, timeD, __icon__))
            return False
        regexs = urlSoup.find('regex')
        pDialog.update(20, 'Parsing info')
        if (not regexs==None) and len(regexs)>0:
            liveLink=    getRegexParsed(urlSoup,link)
        else:
            liveLink=    link

        if len(liveLink)==0:
            timeD = 2000  #in miliseconds
            line1="couldn't read title and link"
            xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, timeD, __icon__))
            return False
            
        timeD = 2000  #in miliseconds
        line1="Resource found,playing now."
        pDialog.update(30, line1)
        liveLink=replaceSettingsVariables(liveLink)
        name+='-'+sc+':'+title
        if (sc=='GLArab' or sc=='Local')  and '$GL-' in liveLink :
            gcid=None
            try:
                gcid = urlSoup.item.glchannelid.text
                if gcid and len(gcid)==0: gcid=None
            except: pass
            liveLink=replaceGLArabVariables(liveLink,pDialog,gcid, title)
            if liveLink=="": return False
        if (sc=='kar' or sc=='Local')  and '$KARLOGINCODE$' in liveLink :
            liveLink=replaceKARVariables(liveLink,pDialog,title)
            if liveLink=="": return False
        if (sc=='yo' or (sc=='Local'  and  ('yoolive.com' in liveLink or 'yooanime.com' in liveLink))) :
            liveLink=replaceYOVariables(liveLink,pDialog,title)
            if liveLink=="": return False
            
        print 'liveLink',liveLink
        pDialog.close()
        listitem = xbmcgui.ListItem( label = str(name), iconImage = "DefaultVideo.png", thumbnailImage = xbmc.getInfoImage( "ListItem.Thumb" ), path=liveLink )
        if not 'plugin.video.f4mTester' in liveLink:
            player = CustomPlayer.MyXBMCPlayer()
            start = time.time() 
            #xbmc.Player().play( liveLink,listitem)
            player.play( liveLink,listitem)
            xbmc.sleep(2000)
            while player.is_active:
                xbmc.sleep(200)
            #return player.urlplayed
            done = time.time()
            elapsed = done - start
            if player.urlplayed and elapsed>=3:
                return True
            else:
                return False
        else:
            xbmc.executebuiltin('XBMC.RunPlugin('+liveLink+')')
            return True
                
    except:
        traceback.print_exc(file=sys.stdout)    
    return False  

def getRegexParsed(regexs, url,cookieJar=None,forCookieJarOnly=False,recursiveCall=False,cachedPages={}, rawPost=False):#0,1,2 = URL, regexOnly, CookieJarOnly

#    cachedPages = {}
    #print 'url',url
    doRegexs = re.compile('\$doregex\[([^\]]*)\]').findall(url)
    print 'doRegexs',doRegexs,regexs

    for rege in doRegexs:
        k=regexs.find("regex",{"name":rege})
        if not k==None:
            cookieJarParam=False
            if k.cookiejar:
                cookieJarParam=k.cookiejar.text;
                if  '$doregex' in cookieJarParam:
                    cookieJar=getRegexParsed(regexs, cookieJarParam,cookieJar,True, True,cachedPages)
                    cookieJarParam=True
                else:
                    cookieJarParam=True
            if cookieJarParam:
                if cookieJar==None:
                    #print 'create cookie jar'
                    import cookielib
                    cookieJar = cookielib.LWPCookieJar()
                    #print 'cookieJar new',cookieJar
            page=''
            try:
                page = k.page.text
            except: pass
            if  '$doregex' in page:
                page=getRegexParsed(regexs, page,cookieJar,recursiveCall=True,cachedPages=cachedPages)
            print 'page',page
            postInput=None
            if k.post:
                postInput = k.post.text
                if  '$doregex' in postInput:
                    postInput=getRegexParsed(regexs, postInput,cookieJar,recursiveCall=True,cachedPages=cachedPages)
                print 'post is now',postInput
            
            if k.rawpost:
                postInput = k.rawpost.text
                if  '$doregex' in postInput:
                    postInput=getRegexParsed(regexs, postInput,cookieJar,recursiveCall=True,cachedPages=cachedPages,rawPost=True)
                print 'rawpost is now',postInput    
            link=''    
            if not page=='' and page in cachedPages and forCookieJarOnly==False :
                link = cachedPages[page]
            else:
                if page.startswith('http'):
                    print 'Ingoring Cache',page
            
                    if '$epoctime$' in page:
                        page=page.replace('$epoctime$',getEpocTime())
                    req = urllib2.Request(page)
                    
                    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:14.0) Gecko/20100101 Firefox/14.0.1')
                    if k.referer:
                        req.add_header('Referer', k.referer.text)
                    if k.agent:
                        req.add_header('User-agent', k.agent.text)

                    if not cookieJar==None:
                        #print 'cookieJarVal',cookieJar
                        cookie_handler = urllib2.HTTPCookieProcessor(cookieJar)
                        opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
                        opener = urllib2.install_opener(opener)
                    #print 'after cookie jar'

                    post=None
                    if postInput and not k.rawpost:
                        postData=postInput
                        splitpost=postData.split(',');
                        post={}
                        for p in splitpost:
                            n=p.split(':')[0];
                            v=p.split(':')[1];
                            post[n]=v
                        post = urllib.urlencode(post)
                        
                    if postInput and k.rawpost:
                        post=postInput

                    if post:
                        response = urllib2.urlopen(req,post)
                    else:
                        response = urllib2.urlopen(req)

                    link = response.read()
                    link=javascriptUnEscape(link)

                    response.close()
                    cachedPages[page] = link
                    if forCookieJarOnly:
                        return cookieJar# do nothing
                elif not page.startswith('http'):
                    if page.startswith('$pyFunction:'):
                        val=doEval(page.split('$pyFunction:')[1],'',cookieJar )
                        if forCookieJarOnly:
                            return cookieJar# do nothing
                        link=val
                    else:
                        link=page
            
            expres=k.expres.text
            if  '$doregex' in expres:
                expres=getRegexParsed(regexs, expres,cookieJar,recursiveCall=True,cachedPages=cachedPages)
                        
            print 'link',link
            print expres
            if not expres=='':
                if expres.startswith('$pyFunction:'):
                    val=doEval(expres.split('$pyFunction:')[1],link, cookieJar)
                    url = url.replace("$doregex[" + rege + "]", val)
                else:
                    if not link=='': 
                        reg = re.compile(expres).search(link)
                        val=reg.group(1).strip()

                    else:
                        val=expres
                    if k.rawpost:
                        print 'rawpost'
                        val=urllib.quote_plus(val)
                    if k.htmlunescape:
                            #val=urllib.unquote_plus(val)
                        import HTMLParser
                        val=HTMLParser.HTMLParser().unescape(val)
                        
                    url = url.replace("$doregex[" + rege + "]",val )
                        
            else:
                url = url.replace("$doregex[" + rege + "]", '')
            
            if '$epoctime$' in url:
                url=url.replace('$epoctime$',getEpocTime())
            if '$GUID$' in url:
                import uuid
                url=url.replace('$GUID$',str(uuid.uuid1()).upper())
            if '$get_cookies$' in url:
                url=url.replace('$get_cookies$',getCookiesString(cookieJar))   
            
            if recursiveCall: return url
    print 'final url',url
    return url
def getCookiesString(cookieJar):
    try:
        cookieString=""
        for index, cookie in enumerate(cookieJar):
            cookieString+=cookie.name + "=" + cookie.value +";"
    except: pass
    print 'cookieString',cookieString
    return cookieString
    
def getEpocTime():
    import time
    return str(int(time.time()*1000))
    
def javascriptUnEscape(str):
	js=re.findall('unescape\(\'(.*?)\'',str)
	print 'js',js
	if (not js==None) and len(js)>0:
		for j in js:
			#print urllib.unquote(j)
			str=str.replace(j ,urllib.unquote(j))
	return str
    
def doEval(fun_call,page_data=None,Cookie_Jar=None):
    ret_val=''
    #if profile not in sys.path:
    #    sys.path.append(profile)
    
    print fun_call
    try:
        py_file='import '+fun_call.split('.')[0]
        #print py_file
        exec( py_file)
    except: pass
    
    exec ('ret_val='+fun_call)
    #exec('ret_val=1+1')
    print 'ret_val',ret_val
    return str(ret_val)
    
def replaceSettingsVariables(str):
    retVal=str
    if '$setting' in str:
        matches=re.findall('\$(setting_.*?)\$', str)
        for m in matches:
            setting_val=selfAddon.getSetting( m )
            retVal=retVal.replace('$'+m+'$',setting_val)
    return retVal


def send_web_socket(Cookie_Jar,url_to_call):
    try:
        import urllib2
        import base64
        import uuid
        req = urllib2.Request(url_to_call)

        str_guid=str(uuid.uuid1()).upper()
        str_guid=base64.b64encode(str_guid)
        req.add_header('Connection', 'Upgrade')
        req.add_header('Upgrade', 'websocket')

        req.add_header('Sec-WebSocket-Key', str_guid)
        req.add_header('Origin','http://www.streamafrik.com')
        req.add_header('Pragma','no-cache')
        req.add_header('Cache-Control','no-cache')
        req.add_header('Sec-WebSocket-Version', '13')
        req.add_header('Sec-WebSocket-Extensions', 'permessage-deflate; client_max_window_bits, x-webkit-deflate-frame')
        req.add_header('User-Agent','Mozilla/5.0 (iPhone; CPU iPhone OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B554a Safari/9537.53')
        cookie_handler = urllib2.HTTPCookieProcessor(Cookie_Jar)
        opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
        opener = urllib2.install_opener(opener)
        from keepalive import HTTPHandler
        keepalive_handler = HTTPHandler()
        opener = urllib2.build_opener(keepalive_handler)
        urllib2.install_opener(opener)
        urllib2.urlopen(req)
        response.close()
        return ''
    except: traceback.print_exc(file=sys.stdout)
    return ''

def get_dag_url(page_data):
    print 'get_dag_url',page_data
    if page_data.startswith('http://dag.total-stream.net'):
        headers=[('User-Agent','Verismo-BlackUI_(2.4.7.5.8.0.34)')]
        page_data=getUrl(page_data,headers=headers);

    if '127.0.0.1' in page_data:
        return revist_dag(page_data)
    elif re_me(page_data, 'wmsAuthSign%3D([^%&]+)') != '':
        final_url = re_me(page_data, '&ver_t=([^&]+)&') + '?wmsAuthSign=' + re_me(page_data, 'wmsAuthSign%3D([^%&]+)') + '==/mp4:' + re_me(page_data, '\\?y=([^&]+)&')
    else:
        final_url = re_me(page_data, 'href="([^"]+)"[^"]+$')
        if len(final_url)==0:
            final_url=page_data
    final_url = final_url.replace(' ', '%20')
    return final_url

def re_me(data, re_patten):
    match = ''
    m = re.search(re_patten, data)

    if m != None:
        match = m.group(1)
    else:
    
        match = ''
    return match

def revist_dag(page_data):
    final_url = ''
    if '127.0.0.1' in page_data:
        final_url = re_me(page_data, '&ver_t=([^&]+)&') + ' live=true timeout=15 playpath=' + re_me(page_data, '\\?y=([a-zA-Z0-9-_\\.@]+)')
        
    if re_me(page_data, 'token=([^&]+)&') != '':
        final_url = final_url + '?token=' + re_me(page_data, 'token=([^&]+)&')
    elif re_me(page_data, 'wmsAuthSign%3D([^%&]+)') != '':
        final_url = re_me(page_data, '&ver_t=([^&]+)&') + '?wmsAuthSign=' + re_me(page_data, 'wmsAuthSign%3D([^%&]+)') + '==/mp4:' + re_me(page_data, '\\?y=([^&]+)&')
    else:
        final_url = re_me(page_data, 'HREF="([^"]+)"')

    if 'dag1.asx' in final_url:
        return get_dag_url(final_url)

    if 'devinlivefs.fplive.net' not in final_url:
        final_url = final_url.replace('devinlive', 'flive')
    return final_url


def get_unwise( str_eval):
    page_value=""
    try:        
        ss="w,i,s,e=("+str_eval+')' 
        exec (ss)
        page_value=unwise_func(w,i,s,e)
    except: traceback.print_exc(file=sys.stdout)
    #print 'unpacked',page_value
    return page_value
    
def unwise_func( w, i, s, e):
    lIll = 0;
    ll1I = 0;
    Il1l = 0;
    ll1l = [];
    l1lI = [];
    while True:
        if (lIll < 5):
            l1lI.append(w[lIll])
        elif (lIll < len(w)):
            ll1l.append(w[lIll]);
        lIll+=1;
        if (ll1I < 5):
            l1lI.append(i[ll1I])
        elif (ll1I < len(i)):
            ll1l.append(i[ll1I])
        ll1I+=1;
        if (Il1l < 5):
            l1lI.append(s[Il1l])
        elif (Il1l < len(s)):
            ll1l.append(s[Il1l]);
        Il1l+=1;
        if (len(w) + len(i) + len(s) + len(e) == len(ll1l) + len(l1lI) + len(e)):
            break;
        
    lI1l = ''.join(ll1l)#.join('');
    I1lI = ''.join(l1lI)#.join('');
    ll1I = 0;
    l1ll = [];
    for lIll in range(0,len(ll1l),2):
        #print 'array i',lIll,len(ll1l)
        ll11 = -1;
        if ( ord(I1lI[ll1I]) % 2):
            ll11 = 1;
        #print 'val is ', lI1l[lIll: lIll+2]
        l1ll.append(chr(    int(lI1l[lIll: lIll+2], 36) - ll11));
        ll1I+=1;
        if (ll1I >= len(l1lI)):
            ll1I = 0;
    ret=''.join(l1ll)
    if 'eval(function(w,i,s,e)' in ret:
        print 'STILL GOing'
        ret=re.compile('eval\(function\(w,i,s,e\).*}\((.*?)\)').findall(ret)[0] 
        return get_unwise(ret)
    else:
        print 'FINISHED'
        return ret

    
def get_unpacked( page_value, regex_for_text='', iterations=1, total_iteration=1):
    try:        
        if page_value.startswith("http"):
            page_value= getUrl(page_value)
        print 'page_value',page_value
        if regex_for_text and len(regex_for_text)>0:
            page_value=re.compile(regex_for_text).findall(page_value)[0] #get the js variable

        page_value=unpack(page_value,iterations,total_iteration)
    except: traceback.print_exc(file=sys.stdout)
    print 'unpacked',page_value
    return page_value

def unpack(sJavascript,iteration=1, totaliterations=2  ):
    print 'iteration',iteration
    if sJavascript.startswith('var _0xcb8a='):
        aSplit=sJavascript.split('var _0xcb8a=')
        ss="myarray="+aSplit[1].split("eval(")[0]
        exec(ss)
        a1=62
        c1=int(aSplit[1].split(",62,")[1].split(',')[0])
        p1=myarray[0]
        k1=myarray[3]
        with open('temp file'+str(iteration)+'.js', "wb") as filewriter:
            filewriter.write(str(k1))
        #aa=1/0
    else:

        aSplit = sJavascript.split("rn p}('")
        print aSplit
        
        p1,a1,c1,k1=('','0','0','')
     
        ss="p1,a1,c1,k1=('"+aSplit[1].split(".spli")[0]+')' 
        exec(ss)
    k1=k1.split('|')
    aSplit = aSplit[1].split("))'")
#    print ' p array is ',len(aSplit)
#   print len(aSplit )

    #p=str(aSplit[0]+'))')#.replace("\\","")#.replace('\\\\','\\')

    #print aSplit[1]
    #aSplit = aSplit[1].split(",")
    #print aSplit[0] 
    #a = int(aSplit[1])
    #c = int(aSplit[2])
    #k = aSplit[3].split(".")[0].replace("'", '').split('|')
    #a=int(a)
    #c=int(c)
    
    #p=p.replace('\\', '')
#    print 'p val is ',p[0:100],'............',p[-100:],len(p)
#    print 'p1 val is ',p1[0:100],'............',p1[-100:],len(p1)
    
    #print a,a1
    #print c,a1
    #print 'k val is ',k[-10:],len(k)
#    print 'k1 val is ',k1[-10:],len(k1)
    e = ''
    d = ''#32823

    #sUnpacked = str(__unpack(p, a, c, k, e, d))
    sUnpacked1 = str(__unpack(p1, a1, c1, k1, e, d,iteration))
    
    #print sUnpacked[:200]+'....'+sUnpacked[-100:], len(sUnpacked)
#    print sUnpacked1[:200]+'....'+sUnpacked1[-100:], len(sUnpacked1)
    
    #exec('sUnpacked1="'+sUnpacked1+'"')
    if iteration>=totaliterations:
#        print 'final res',sUnpacked1[:200]+'....'+sUnpacked1[-100:], len(sUnpacked1)
        return sUnpacked1#.replace('\\\\', '\\')
    else:
#        print 'final res for this iteration is',iteration
        return unpack(sUnpacked1,iteration+1)#.replace('\\', ''),iteration)#.replace('\\', '');#unpack(sUnpacked.replace('\\', ''))

def __unpack(p, a, c, k, e, d, iteration,v=1):

    #with open('before file'+str(iteration)+'.js', "wb") as filewriter:
    #    filewriter.write(str(p))
    while (c >= 1):
        c = c -1
        if (k[c]):
            aa=str(__itoaNew(c, a))
            #re.sub('\\b' + aa +'\\b', k[c], p) THIS IS Bloody slow!
            if v==1:
                p=re.sub('\\b' + aa +'\\b', k[c], p)# THIS IS Bloody slow!
            else:
                p=findAndReplaceWord(p,aa,k[c])
            #p=findAndReplaceWord(p,aa,k[c])

            
    #with open('after file'+str(iteration)+'.js', "wb") as filewriter:
    #    filewriter.write(str(p))
    return p

#
#function equalavent to re.sub('\\b' + aa +'\\b', k[c], p)
def findAndReplaceWord(source_str, word_to_find,replace_with):
    splits=None
    splits=source_str.split(word_to_find)
    if len(splits)>1:
        new_string=[]
        current_index=0
        for current_split in splits:
            #print 'here',i
            new_string.append(current_split)
            val=word_to_find#by default assume it was wrong to split

            #if its first one and item is blank then check next item is valid or not
            if current_index==len(splits)-1:
                val='' # last one nothing to append normally
            else:
                if len(current_split)==0: #if blank check next one with current split value
                    if ( len(splits[current_index+1])==0 and word_to_find[0].lower() not in 'abcdefghijklmnopqrstuvwxyz1234567890_') or (len(splits[current_index+1])>0  and splits[current_index+1][0].lower() not in 'abcdefghijklmnopqrstuvwxyz1234567890_'):# first just just check next
                        val=replace_with
                #not blank, then check current endvalue and next first value
                else:
                    if (splits[current_index][-1].lower() not in 'abcdefghijklmnopqrstuvwxyz1234567890_') and (( len(splits[current_index+1])==0 and word_to_find[0].lower() not in 'abcdefghijklmnopqrstuvwxyz1234567890_') or (len(splits[current_index+1])>0  and splits[current_index+1][0].lower() not in 'abcdefghijklmnopqrstuvwxyz1234567890_')):# first just just check next
                        val=replace_with
                        
            new_string.append(val)
            current_index+=1
        #aaaa=1/0
        source_str=''.join(new_string)
    return source_str        

def __itoa(num, radix):
#    print 'num red',num, radix
    result = ""
    if num==0: return '0'
    while num > 0:
        result = "0123456789abcdefghijklmnopqrstuvwxyz"[num % radix] + result
        num /= radix
    return result
	
def __itoaNew(cc, a):
    aa="" if cc < a else __itoaNew(int(cc / a),a) 
    cc = (cc % a)
    bb=chr(cc + 29) if cc> 35 else str(__itoa(cc,36))
    return aa+bb


def getCookiesString(cookieJar):
    try:
        cookieString=""
        for index, cookie in enumerate(cookieJar):
            cookieString+=cookie.name + "=" + cookie.value +";"
    except: pass
    print 'cookieString',cookieString
    return cookieString

def getUrl(url, cookieJar=None,post=None, timeout=20, headers=None, returnResponse=False, noredirect=False):

    cookie_handler = urllib2.HTTPCookieProcessor(cookieJar)
    opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
#    opener = urllib2.install_opener(opener)
    
    req = urllib2.Request(url)
    req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36')
    if headers:
        for h,hv in headers:
            req.add_header(h,hv)

    response = opener.open(req,post,timeout=timeout)
    if returnResponse: return response
    link=response.read()
    response.close()
    return link;

#copies from lamda's implementation
def get_ustream(url):
    try:
        for i in range(1, 51):
            result = getUrl(url)
            if "EXT-X-STREAM-INF" in result: return url
            if not "EXTM3U" in result: return
            xbmc.sleep(2000)
        return
    except:
        return
        
def get_saw_rtmp(page_value, referer=None):
    if referer:
        referer=[('Referer',referer)]
    if page_value.startswith("http"):
        page_url=page_value
        page_value= getUrl(page_value,headers=referer)
    str_pattern="(eval\(function\(p,a,c,k,e,d.*)"

    reg_res=re.compile(str_pattern).findall(page_value)
    r=""
    if reg_res and len(reg_res)>0:
        for v in reg_res:
            r1=get_unpacked(v)
            r2=re_me(r1,'\'(.*?)\'')
            if 'unescape' in r1:
                r1=urllib.unquote(r2)
            r+=r1+'\n'
        print 'final value is ',r
        
        page_url=re_me(r,'src="(.*?)"')
        
        page_value= getUrl(page_url,headers=referer)
        
    print page_value

    rtmp=re_me(page_value,'streamer\'.*?\'(.*?)\'\)')
    playpath=re_me(page_value,'file\',\s\'(.*?)\'')

    
    return rtmp+' playpath='+playpath +' pageUrl='+page_url
    
def get_leton_rtmp(page_value, referer=None):
    if referer:
        referer=[('Referer',referer)]
    if page_value.startswith("http"):
        page_value= getUrl(page_value,headers=referer)
    str_pattern="var a = (.*?);\s*var b = (.*?);\s*var c = (.*?);\s*var d = (.*?);\s*var f = (.*?);\s*var v_part = '(.*?)';"
    reg_res=re.compile(str_pattern).findall(page_value)[0] 

    a,b,c,d,f,v=(reg_res)
    f=int(f)
    a=int(a)/f
    b=int(b)/f
    c=int(c)/f
    d=int(d)/f

    ret= 'rtmp://' + str(a) + '.' + str(b) + '.' + str(c) + '.' + str(d) + v;
    return ret
    

def get_packed_iphonetv_url(page_data):
    import re,base64,urllib; 
    s=page_data
    while 'geh(' in s:
        if s.startswith('lol('): s=s[5:-1]    
    #		print 's is ',s
        s=re.compile('"(.*?)"').findall(s)[0]; 
        s=  base64.b64decode(s); 
        s=urllib.unquote(s); 
    print s
    return s    

    
def decrypt_vaughnlive(encrypted):
    retVal=""
    for val in encrypted.split(':'):
        retVal+=chr(int(val.replace("0m0",""))/84/5)
    return retVal

def replaceGLArabVariables(link, d,gcid, title):
    try:
        GLArabUserName=selfAddon.getSetting( "GLArabUserName" )
        GLArabUserPwd=selfAddon.getSetting( "GLArabUserPwd" )
        GLArabServerLOW=selfAddon.getSetting( "GLArabServerLOW" )
        GLArabServerHD=selfAddon.getSetting( "GLArabServerHD" )
        GLArabServerMED=selfAddon.getSetting( "GLArabServerMED" )
        GLArabServerLR=selfAddon.getSetting( "GLArabServerLR" )
        GLArabServerLOWNP=selfAddon.getSetting( "GLArabServerLOWNP" )
        
        glLocalProxy=selfAddon.getSetting( "isGLProxyEnabled" )=="true" and 'Proxy' in title
        glproxyCommon=selfAddon.getSetting( "isGLCommonProxyEnabled" )=="true" and 'Proxy' in title
    
        glProxyAddress=selfAddon.getSetting( "GLproxyName" )
        if glProxyAddress=="": glProxyAddress="127.0.0.1"
        pattern='channel=(.*?)\&'
        link=link.replace('$GLProxyIP$',glProxyAddress)
        ProxyCall=True
        if 'Proxy' not in title: 
            print 'Not a proxy'
            glLocalProxy=False
            glproxyCommon=False
            pattern='7777\/(.*?)\.m3u8'
            GLArabServerLOW=GLArabServerLOWNP
            print 'low nonproxy',GLArabServerLOW
            ProxyCall=False
        elif glLocalProxy==False and glproxyCommon==False:
            print 'Proxy but no proxy call'
            return ''
        

        videoPath='KuwaitSpace_Med'
        try:            
            videoPath=re.compile(pattern).findall(link)[0]
        except: pass
            
        print 'videoPath',videoPath
        if GLArabServerLOW=="": GLArabServerLOW="Try All"
        if GLArabServerHD=="": GLArabServerHD="Try All"
        if GLArabServerMED=="": GLArabServerMED="Try All"        
        if GLArabServerLR=="": GLArabServerLR="Try All"        

        GLArabQuality=selfAddon.getSetting( "GLArabQuality" )
        tryLogin=True
        if GLArabUserName=="" or GLArabUserPwd=="":# or '$GL-IPHD$' not in link  or '$GL-IPMED$'  not in link:
            tryLogin=False
            timeD = 2000  #in miliseconds
            line1="Login not defined, using default login and low quality"
            GLArabQuality=""
            #xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, timeD, __icon__))
            print line1

        #if GLArabServer=="": GLArabServer="Low 38.99.146.43:7777"
        #GLArabServer=GLArabServer.split(' ')[1]
        #GLArabQuality="" if GLArabQuality=="Low" or GLArabQuality=="" else '_'+GLArabQuality
        import cookielib
        cookieJar = cookielib.LWPCookieJar()
        #def getUrl(url, cookieJar=None,post=None, timeout=20, headers=None):
        
        try:
            if tryLogin:
                mainpage=getUrl('http://www.glarab.com/',cookieJar)
                evalidation=re.compile(' id="__EVENTVALIDATION" value="(.*?)"').findall(mainpage)[0]
                vstate=re.compile('id="__VIEWSTATE" value="(.*?)"').findall(mainpage)[0]  

                post={'pageHeader$ScriptManager1':'pageHeader$UpdatePanel1|pageHeader$buttonLogin','__EVENTTARGET':'','__EVENTARGUMENT':'','__VIEWSTATE':vstate,'__EVENTVALIDATION':evalidation,'pageHeader$txtUsername':GLArabUserName,'pageHeader$txtPassword':GLArabUserPwd,'pageHeader$buttonLogin':' '}
                post = urllib.urlencode(post)
                getUrl('http://www.glarab.com/homepage.aspx',cookieJar,post)
            else:
                getUrl('http://www.glarab.com/',cookieJar)
        except:
            print 'login or accessing the site failed.. continuing'
            traceback.print_exc(file=sys.stdout)
        
        if gcid or ProxyCall==False:
            if gcid:
                gcUrl='https://apps.glwiz.com:448/uniwebappandroidads/(S(g01ykv45pojkhpzwap1u14dy))/ajax.ashx?channel=tv&chid=%s&'%gcid
                print gcUrl,'gcUrl'
                gcidhtml=getUrl(gcUrl)
                print gcidhtml
                patt='makeHttpRequestNoCache\\(\'(.*?)\''
                gcurl='https://apps.glwiz.com:448/uniwebappandroidads/(S(g01ykv45pojkhpzwap1u14dy))/'+ re.compile(patt).findall(gcidhtml)[0] 
                print 'gcurl',gcurl
                gcurl=gcurl.replace(' ','%20')
            else:
                gcurl='https://apps.glwiz.com:448/uniwebappandroidads/(S(0mdxhq55vlua3zy1wfg4oooz))/ajax.ashx?stream=tv&ppoint=0&chid=0&chname=&clustername=zixi-mobile&'
                
            sessionpage=getUrl(gcurl,cookieJar)
            
            print sessionpage
            session=sessionpage.split(':')[2]
            sessionserver=sessionpage.split(':')[0].replace(':2077','')
         
        elif glLocalProxy or glproxyCommon:
            gcUrl=base64.b64decode('aHR0cHM6Ly9hcHBzLmdsd2l6LmNvbTo0NDgvVW5pV2ViQXBwQW5kcm9pZC9hamF4LmFzaHg/c3RyZWFtPXR2JnBwb2ludD1NQkNNYXNlckRyYW1hX0hpZ2gmY2hpZD0zMDM2MDAmY2huYW1lPU1CQyUyME1hc2VyJTIwRHJhbWEmY2x1c3Rlcm5hbWU9eml4aSY=')
            #print gcUrl,'gcUrl'
            sessionpage=getUrl(gcUrl)            
            print sessionpage
            session=sessionpage.split(':')[2]
            sessionserver=sessionpage.split(':')[0].replace(':2077','')
        else:
            hell_pat='hello-data", "(.*?)"'
            header=[('Referer','http://www.glarab.com/homepage.aspx')]
            hellHtml=getUrl('http://www.glarab.com/js/glapi.ashx ',cookieJar,headers=header)

            hello_data=re.compile(hell_pat).findall(hellHtml)[0] 
            header=[('X-hello-data',hello_data),('Referer','http://www.glarab.com/player.aspx')]
            
            sessionpage=getUrl('http://www.glarab.com/ajax.aspx?stream=live&type=reg&ppoint=%s'%videoPath,cookieJar,headers=header)
            print sessionpage
            session=sessionpage.split('|')[1]
            sessionserver=sessionpage.split('|')[2].replace(':2077','')
 
            
        serverPatern=''
        serverAddress=''
        type='low'
        if '$GL-IPLOW$' in link or 'Low' in title:
            if not ProxyCall:
                serverPatern='GLArabServerLOWNP.*values="(.*?)"'
            else:            
                serverPatern='GLArabServerLOW.*values="(.*?)"'
            link=link.replace('$GL-IPLOW$',GLArabServerLOW)
            serverAddress=GLArabServerLOW
            type='low'

        if  '$GL-IPHD$' in link or 'High' in title or 'HD' in title:
            print 'i am here',GLArabServerHD
            serverPatern='GLArabServerHD.*values="(.*?)"'
            link=link.replace('$GL-IPHD$',GLArabServerHD)
            serverAddress=GLArabServerHD
            type='hd'

            
        if '$GL-IPMED$' in link or 'Med' in title:
            serverPatern='GLArabServerMED.*values="(.*?)"'
            link=link.replace('$GL-IPMED$',GLArabServerMED)
            serverAddress=GLArabServerMED
            print GLArabServerMED,'GLArabServerMED  '
            type='med'
            
        if '$GL-IPLR$' in link or 'LR' in title:
            serverPatern='GLArabServerLR.*values="(.*?)"'
            link=link.replace('$GL-IPLR$',GLArabServerLR)
            serverAddress=GLArabServerLR
            print GLArabServerLR,'GLArabServerLR  '
            type='lr'
        
        import random
        token=str(int(152 +random.random() * 99999));

        GlUser=token#base64.b64decode('MzM4OA==')
        link=link.replace('$GL-Qlty$',GLArabQuality)
        link=link.replace('$GL-Sesession$',session)
        link=link.replace('$GL-User$',GlUser)
        print 'the links is ',link
        

                
                                           
        
        if 'Try All' in link:
            fileName=communityStreamPath+'/../settings.xml'
            settingsData= open(fileName, "r").read()
            #print settingsData
            servers=re.compile(serverPatern).findall(settingsData)[0] 
            servers=servers.replace('Disabled|Try All|','').split('|')  
            #print servers
            
            if 1==1:#not glProxy:
                servers.insert(0,sessionserver);
                print 'new',servers
                i=0
                for server in servers:
                    i+=1
                    if d.iscanceled(): return ""
                    d.update(30+(50*1/len(servers)), 'Trying server %s'%server)

                    try:
                        finalUrl=link.replace('Try All',server)
                        if not glLocalProxy:
                            ret=getUrl(finalUrl,timeout=8);
                            if 'm3u8?' in ret:
                                link=finalUrl
                                d.update(90, 'Working server found %s'%server)
                                return link
                                break
                        else:
                            res=getUrl(finalUrl,timeout=8,returnResponse=True);
                            data=res.read(2000)
                            if data and len(data)>1000:
                                print 'working proxy found',finalUrl
                                d.update(90, 'Working server found %s'%server)
                                link=finalUrl
                                return link;#just return
                                break                            
                    except: pass
                    
        if glproxyCommon:
            try:
                #4500/channel.flv?server=8.21.48.20&channel=AlJadeed_HD
                newLink='http://178.33.241.201:4500/channel.flv?server=8.21.48.19&channel=%s'%videoPath
                print 'trying common proxy here',newLink
                res=getUrl(newLink,timeout=15,returnResponse=True);
                data=res.read(2000)
                print 'data here',len(data),repr(data)
                if data and len(data)>1000:
                    print 'custom proxy found',newLink
                    d.update(90, 'Working server found (Common proxy)')
                    return newLink
            except: pass            

         
        #if glProxy and 'Try All' in link: 
        #    link=link.replace('Try All',serverAddress)
#            if 'High' in title or 'HD' in title:
#                link=link.replace('Try All',serverAddress)
#            else:
 #               link=link.replace('Try All',sessionserver.replace(':7777',''))
            #if type=='low' or type=='med' or type=='lr':        
            #    link=getProxyLink(glProxyAddress,sessionserver.replace(':7777',''),videoPath,session)
            #else:    
            #    link=getProxyLink(glProxyAddress,serverAddress.replace(':7777',''),videoPath,session)
         
        if 'Try All' in link: 
            print 'no working link',link
            link=''
        return link
    except:
        traceback.print_exc(file=sys.stdout)
        return link

def getProxyLink(proxy,server,video_path,session):
    return 'http://%s:4500/channel.flv?server=%s&channel=%s&port=2077&session=%s'%(proxy,server,video_path,session)

def replaceKARVariables(liveLink,pDialog,title):
    karUser=selfAddon.getSetting( "KARUSER" )
    karPwd=selfAddon.getSetting( "KARPWD" )

    if karUser=="" or karPwd=="":
        return ""
    cfile = communityStreamPath+'/karLoginCookie.lwp'
    cj=getCookieJar(cfile)
    htmlD=getUrl('http://karimos-sat.com/index-home.php', cookieJar=cj,timeout=20)
    if not (len(htmlD)>0 and 'user_token' in htmlD):
        post = urllib.urlencode({'submitted':1,'username':karUser,'password':karPwd,'Submit':'Submit'})
        htmlD=getUrl('http://karimos-sat.com/loginuser.php', cookieJar=cj,post=post,timeout=20)

    code_pat='d="user_token" >(.*?)<'        
    reg_code=re.compile(code_pat).findall(htmlD)[0]
    saveCookieJar(cj,cfile)
    return liveLink.replace('$KARLOGINCODE$',reg_code)

def replaceYOVariables(liveLink,pDialog,title):
    if not liveLink.endswith('.php'):
        return liveLink
    sUser=selfAddon.getSetting( "YOUSER" )
    sPwd=selfAddon.getSetting( "YOPWD" )

    if sUser=="" or sPwd=="":
        return ""
    cfile = communityStreamPath+'/yoLoginCookie.lwp'
    cj=getCookieJar(cfile)
    htmlD=getUrl('http://yooanime.com/index.php', cookieJar=cj,timeout=20)
    if  'Log In | Register' in htmlD:
        post = urllib.urlencode({'rememberMe':1,'username':sUser,'password':sPwd,'submit':'Login'})
        htmlD=getUrl('http://yooanime.com/index.php', cookieJar=cj,post=post,timeout=20)

    page_data=getUrl(liveLink, cookieJar=cj,timeout=20)
    code_pat='\[\{file:"(.*?)"'        
    reg_code=re.compile(code_pat).findall(page_data)[0]
    saveCookieJar(cj,cfile)
    if reg_code.startswith('rtmp'):
        reg_code+=' timeout=10'
    return reg_code
    
def getCookieJar(cfile):
    cookieJar=None

    try:
        cookieJar = cookielib.LWPCookieJar()
        cookieJar.load(cfile,ignore_discard=True)
    except: 
        cookieJar=None

    if not cookieJar:
        cookieJar = cookielib.LWPCookieJar()
    return cookieJar
        
def saveCookieJar(cookieJar,COOKIEFILE):
	try:
		cookieJar.save(COOKIEFILE,ignore_discard=True)
	except: pass
