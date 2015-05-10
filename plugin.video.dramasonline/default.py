import xbmc, xbmcgui, xbmcplugin
import urllib2,urllib,cgi, re, urlresolver, sys
import urlparse
import HTMLParser
import xbmcaddon
from operator import itemgetter
import traceback,os

__addon__       = xbmcaddon.Addon()
__addonname__   = __addon__.getAddonInfo('name')
__icon__        = __addon__.getAddonInfo('icon')
addon_id = 'plugin.video.dramasonline'
selfAddon = xbmcaddon.Addon(id=addon_id)
  
 
mainurl='http://www.dramasonline.com/'
liveURL='http://www.zemtv.com/live-pakistani-news-channels/'

tabURL ='http://www.eboundservices.com:8888/users/rex/m_live.php?app=%s&stream=%s'

def addLink(name,url,iconimage):
	ok=True
	liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
	return ok

def Colored(text = '', colorid = '', isBold = False):
	if colorid == 'ZM':
		color = 'FF11b500'
	elif colorid == 'EB':
		color = 'FFe37101'
	elif colorid == 'bold':
		return '[B]' + text + '[/B]'
	else:
		color = colorid
		
	if isBold == True:
		text = '[B]' + text + '[/B]'
	return '[COLOR ' + color + ']' + text + '[/COLOR]'	
	
def addDir(name,url,mode,iconimage	,showContext=False, showLiveContext=False,isItFolder=True):
#	print name
#	name=name.decode('utf-8','replace')
	h = HTMLParser.HTMLParser()
	name= h.unescape(name.decode("utf8")).encode("ascii","ignore")
	#print  name
	#print url
	#print iconimage
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True
#	print iconimage
	liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	liz.setInfo( type="Video", infoLabels={ "Title": name } )

	if showContext==True:
		cmd1 = "XBMC.RunPlugin(%s&linkType=%s)" % (u, "DM")
		cmd2 = "XBMC.RunPlugin(%s&linkType=%s)" % (u, "LINK")
		cmd3 = "XBMC.RunPlugin(%s&linkType=%s)" % (u, "Youtube")
		liz.addContextMenuItems([('Play Youtube video',cmd3),('Play DailyMotion video',cmd1),('Play Tune.pk video',cmd2)])
	
	if showLiveContext==True:
		cmd1 = "XBMC.RunPlugin(%s&linkType=%s)" % (u, "RTMP")
		cmd2 = "XBMC.RunPlugin(%s&linkType=%s)" % (u, "HTTP")
		liz.addContextMenuItems([('Play RTMP Steam (flash)',cmd1),('Play Http Stream (ios)',cmd2)])
	
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=isItFolder)
	return ok
	


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




def Addtypes():
	baseLink = 'http://www.dramasonline.com/%s-latest-dramas-episodes-online/'
	#2 is series=3 are links
	addDir('All Recent Episodes' ,'http://www.dramasonline.com/' ,3,'') #links 
	addDir('HumTv Shows', baseLink % 'hum-tv' ,2,'')
	addDir('GeoTv Shows', baseLink % 'geo-tv' ,2,'')
	addDir('AryDigital Shows', baseLink % 'ary-digital-tv' ,2,'')
	addDir('Hum Sitaray Shows', baseLink % 'hum-sitaray' ,2,'')
	addDir('Express Shows', baseLink % 'express-entertainment' ,2,'')
	addDir('APlus Shows', baseLink % 'aplus-entertainment' ,2,'')
	addDir('Urdu1 Shows', baseLink % 'urdu-1' ,2,'')
	addDir('Teleplays' ,'http://www.dramasonline.com/?cat=255' ,3,'')# these are is links
	addDir('Top Rated Dramas' ,'http://www.dramasonline.com/' ,5,'') # top 
	addDir('Live Channels' ,'http://www.dramasonline.com/category/live-channels/' ,6,'') ##
	addDir('Settings' ,'http://www.dramasonline.com/category/live-channels/' ,8,'',isItFolder=False) ##
	return

def ShowSettings(Fromurl):
	selfAddon.openSettings()

def AddSeries(Fromurl):
	print Fromurl
	req = urllib2.Request(Fromurl)
	req.add_header('User-Agent','Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	#print link
#	print "addshows"
#	match=re.compile('<param name="URL" value="(.+?)">').findall(link)
#	match=re.compile('<a href="(.+?)"').findall(link)
#	match=re.compile('onclick="playChannel\(\'(.*?)\'\);">(.*?)</a>').findall(link)
#	match =re.findall('onclick="playChannel\(\'(.*?)\'\);">(.*?)</a>', link, re.DOTALL|re.IGNORECASE)
#	match =re.findall('onclick="playChannel\(\'(.*?)\'\);".?>(.*?)</a>', link, re.DOTALL|re.IGNORECASE)
#	match =re.findall('<div class=\"post-title\"><a href=\"(.*?)\".*<b>(.*)<\/b><\/a>', link, re.IGNORECASE)
#	match =re.findall('<img src="(.*?)" alt=".*".+<\/a>\n*.+<div class="post-title"><a href="(.*?)".*<b>(.*)<\/b>', link, re.UNICODE)
	regstring='<a title="(.*?)" href="(.*?)".*?img.*?src="(.*?)" wid'
	optiontype=1
	if 'ary-digital'  in Fromurl or  'aplus-ent'  in Fromurl: 
		regstring='\s*<a href="(.*?)"targe.*?<img.*?alt="(.*?)" src="(.*?)"'
		optiontype=2
		match =re.findall(regstring, link, re.M)
	else:
		match =re.findall(regstring, link, re.M|re.DOTALL)
	#match=re.compile('<a href="(.*?)"targe.*?<img.*?alt="(.*?)" src="(.*?)"').findall(link)
	#print '\n'.join([str(x) for x in match])


	print 'optiontype %s' % optiontype



	for cname in match:

		item_name = name_from_re = cname[optiontype-1]

		name_from_url = cname[0].rstrip('/').split('/')
		# get last part of url
		name_from_url = name_from_url[-1].replace('-', ' ')

		#print '%s - %s' % (item_name, name_from_url)

		if (name_from_url.lower() != name_from_re.lower()):
			item_name = name_from_url

		item_name = item_name.replace('Watch ', '').replace('watch ', '').title()

		print item_name

		if optiontype==2:
			addDir(item_name, cname[0], 3, cname[2])#url,name,jpg#name,url,mode,icon
		else:
			addDir(item_name, cname[1], 3, cname[2])#name,url,img
		
#	<a href="http://www.zemtv.com/page/2/">&gt;</a></li>
#	match =re.findall('<a href="(.*)">&gt;<\/a><\/li>', link, re.IGNORECASE)
	
#	if len(match)==1:
#		addDir('Next Page' ,match[0] ,2,'')
#       print match
	
	return

def TopRatedDramas(Fromurl):
	#print Fromurl
	req = urllib2.Request(Fromurl)
	req.add_header('User-Agent','Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
#	print link
#	print "addshows"
#	match=re.compile('<param name="URL" value="(.+?)">').findall(link)
#	match=re.compile('<a href="(.+?)"').findall(link)
#	match=re.compile('onclick="playChannel\(\'(.*?)\'\);">(.*?)</a>').findall(link)
#	match =re.findall('onclick="playChannel\(\'(.*?)\'\);">(.*?)</a>', link, re.DOTALL|re.IGNORECASE)
#	match =re.findall('onclick="playChannel\(\'(.*?)\'\);".?>(.*?)</a>', link, re.DOTALL|re.IGNORECASE)
#	match =re.findall('<div class=\"post-title\"><a href=\"(.*?)\".*<b>(.*)<\/b><\/a>', link, re.IGNORECASE)
#	match =re.findall('<img src="(.*?)" alt=".*".+<\/a>\n*.+<div class="post-title"><a href="(.*?)".*<b>(.*)<\/b>', link, re.UNICODE)
	regstring='<li><a href="(.*?)".*?>(.*?)<\/a><\/li>'
	match =re.findall(regstring, link, re.M|re.DOTALL)
	#match=re.compile('<a href="(.*?)"targe.*?<img.*?alt="(.*?)" src="(.*?)"').findall(link)
#	print Fromurl

#	print match
	h = HTMLParser.HTMLParser()
#	print 'match',match
	for cname in match:
		addDir(cname[1],cname[0] ,3,'')#url,name,jpg#name,url,mode,icon
		
#	<a href="http://www.zemtv.com/page/2/">&gt;</a></li>
#	match =re.findall('<a href="(.*)">&gt;<\/a><\/li>', link, re.IGNORECASE)
	
#	if len(match)==1:
#		addDir('Next Page' ,match[0] ,2,'')
#       print match
	
	return

def AddEnteries(Fromurl):
	print 'getting enteries %s' % Fromurl

	req = urllib2.Request(Fromurl)
	req.add_header('User-Agent','Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
#	print link
#	print "addshows"
#	match=re.compile('<param name="URL" value="(.+?)">').findall(link)
#	match=re.compile('<a href="(.+?)"').findall(link)
#	match=re.compile('onclick="playChannel\(\'(.*?)\'\);">(.*?)</a>').findall(link)
#	match =re.findall('onclick="playChannel\(\'(.*?)\'\);">(.*?)</a>', link, re.DOTALL|re.IGNORECASE)
#	match =re.findall('onclick="playChannel\(\'(.*?)\'\);".?>(.*?)</a>', link, re.DOTALL|re.IGNORECASE)
#	match =re.findall('<div class=\"post-title\"><a href=\"(.*?)\".*<b>(.*)<\/b><\/a>', link, re.IGNORECASE)
#	match =re.findall('<img src="(.*?)" alt=".*".+<\/a>\n*.+<div class="post-title"><a href="(.*?)".*<b>(.*)<\/b>', link, re.UNICODE)
#	print Fromurl
#	match =re.findall('<div class="videopart">\s*<div class="paneleft">\s*<a class="pthumb" href="(.*?)" title="(.*?)".*?img.*?src="(.*?)" class="attachment-index-post-thumbnail wp-post-image"', link, re.M|re.DOTALL)
	match =re.findall('<div class="video_thumnail_hover" href="#">\s*<a class="pthumb" href="(.*?)" title="(.*?)" ><img alt="" src=".*?hover_bg.png"><\/a>\s*<\/div>\s*<a class="pthumb"\s+href=".*?" title=".*?" ><span><\/span>\s*<img width="\d+" height="\d+" src="(.*?)" class="attachment-index-post-thumbnail wp-post-image".*?\/><\/a>', link, re.M|re.DOTALL)
#	print Fromurl

	#print match
	h = HTMLParser.HTMLParser()

	for cname in match:
		addDir(cname[1] ,cname[0] ,4,cname[2],isItFolder=False)
		
#	<a href="http://www.zemtv.com/page/2/">&gt;</a></li>
	match =re.findall('<link rel=\'next\' href=\'(.*?)\' \/>', link, re.IGNORECASE)
	
	if len(match)==1:
		addDir('Next Page' ,match[0] ,3,'')
#       print match
	
	return
	
def AddChannels(liveURL):
	req = urllib2.Request(liveURL)
	req.add_header('User-Agent','Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
#	print link
#	match=re.compile('<param name="URL" value="(.+?)">').findall(link)
#	match=re.compile('<a href="(.+?)"').findall(link)
#	match=re.compile('onclick="playChannel\(\'(.*?)\'\);">(.*?)</a>').findall(link)
#	match =re.findall('onclick="playChannel\(\'(.*?)\'\);">(.*?)</a>', link, re.DOTALL|re.IGNORECASE)
#	match =re.findall('onclick="playChannel\(\'(.*?)\'\);".?>(.*?)</a>', link, re.DOTALL|re.IGNORECASE)
#	match =re.findall('<div class=\"post-title\"><a href=\"(.*?)\".*<b>(.*)<\/b><\/a>', link, re.IGNORECASE)
#	match =re.findall('<img src="(.*?)" alt=".*".+<\/a>\n*.+<div class="post-title"><a href="(.*?)".*<b>(.*)<\/b>', link, re.UNICODE)

	match =re.findall('<div class="videopart">\s*<div class="paneleft">\s*<a.*?href="(.*?)".*?title="(.*?)".*?<img.*?src="(.*?)"', link,re.M)

	#print match
	#h = HTMLParser.HTMLParser()
	for cname in match:
		addDir(Colored(cname[1],'ZM') ,cname[0] ,7,cname[2], False, True,isItFolder=False)		#name,url,mode,icon

	return	

def AddChannelsFromEbound():
	liveURL='http://eboundservices.com/istream_demo.php'
	req = urllib2.Request(liveURL)
	req.add_header('User-Agent','Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
#	print link
#	match=re.compile('<param name="URL" value="(.+?)">').findall(link)
#	match=re.compile('<a href="(.+?)"').findall(link)
#	match=re.compile('onclick="playChannel\(\'(.*?)\'\);">(.*?)</a>').findall(link)
#	match =re.findall('onclick="playChannel\(\'(.*?)\'\);">(.*?)</a>', link, re.DOTALL|re.IGNORECASE)
#	match =re.findall('onclick="playChannel\(\'(.*?)\'\);".?>(.*?)</a>', link, re.DOTALL|re.IGNORECASE)
#	match =re.findall('<div class=\"post-title\"><a href=\"(.*?)\".*<b>(.*)<\/b><\/a>', link, re.IGNORECASE)
#	match =re.findall('<img src="(.*?)" alt=".*".+<\/a>\n*.+<div class="post-title"><a href="(.*?)".*<b>(.*)<\/b>', link, re.UNICODE)

	match =re.findall('<a href=".*?stream=(.*?)".*?src="(.*?)"', link,re.M)

	#print match
	expressExists=False
	expressCName='express'
	arynewsAdded=False

	#h = HTMLParser.HTMLParser()
	for cname in match:
		addDir(Colored(cname[0].capitalize(),'EB') ,cname[0] ,9,cname[1], False, True,isItFolder=False)		#name,url,mode,icon
		if cname[0]==expressCName:
			expressExists=True
		if cname[0]=='arynews':
			arynewsAdded=True
			
	if not expressExists:
		addDir(Colored('Express Tv','EB') ,'express' ,9,'', False, True,isItFolder=False)		#name,url,mode,icon
	if not arynewsAdded:
		addDir(Colored('Ary News','EB') ,'arynews' ,9,'', False, True,isItFolder=False)		#name,url,mode,icon
		addDir(Colored('Ary Digital','EB') ,'aryentertainment' ,9,'', False, True,isItFolder=False)		#name,url,mode,icon
			
	return		

def Colored(text = '', colorid = '', isBold = False):
	if colorid == 'ZM':
		color = 'FF11b500'
	elif colorid == 'EB':
		color = 'FFe37101'
	elif colorid == 'bold':
		return '[B]' + text + '[/B]'
	else:
		color = colorid
		
	if isBold == True:
		text = '[B]' + text + '[/B]'
	return '[COLOR ' + color + ']' + text + '[/COLOR]'	

def getPlaywireUrl(html, short):
	playURL = None
	newFormat = False

	try:
		match =re.findall('src=".*?(playwire).*?data-publisher-id="(.*?)"\s*data-video-id="(.*?)"',html)

		if len(match):
			playURL=match[0]

		else:
			# try new links
			str = '<script data-config="(http)?...?config.playwire.com.(\d+)\/videos.v2.(\d+)\/'
			match =re.findall(str, html)

			if len(match):
				newFormat = True
				playURL=match[0]

		print playURL
		if short:
			return playURL

		if playURL is None:
			return None

		if newFormat:
			(pp,PubId,videoID)=playURL

			cdnUrl="http://config.playwire.com/%s/videos/v2/%s/manifest.f4m" % (PubId,videoID)
			link=getHtml(cdnUrl)

			str = '<baseURL>\s*(.+)\s*</baseURL>\s*<media url="(.+)" bitrate'
			match =re.findall(str, link)[0]

			playURL ="%s/%s"%(match[0], match[1])

		else:
			(playWireVar,PubId,videoID)=playURL
			cdnUrl="http://cdn.playwire.com/v2/%s/config/%s.json"%(PubId,videoID)
			link=getHtml(cdnUrl)
			playURL ="http://cdn.playwire.com/%s/%s"%(PubId,re.findall('src":".*?mp4:(.*?)"', link)[0])

		print 'Final playURL: %s' % playURL
		return playURL

	except:
		traceback.print_exc(file=sys.stdout)
		return None
		
def getDailyMotionUrl(html, short):
	try:
		match =re.findall('src="(.*?(dailymotion).*?)"',html)
		playURL=match[0][0]
		print playURL
		if short:
			return playURL
		stream_url = urlresolver.HostedMediaFile(playURL).resolve()
		return stream_url
	except:
		print 'Error fetching DailyMotion stream url'
		traceback.print_exc(file=sys.stdout)
		return None

def getTuneTvUrl(html, short):
	try:
		# Find the first match
		playURL =re.search('<strong>Tune\s*[Ff]ull<\/strong>\s*.*?src="(.+embed_player.php\?vid=(\d+).*?)"',html)
		print 'getTuneTvUrl: %s' % playURL
		if short:
			return playURL

		if playURL is None:
			return None

		print 'match: ' + playURL.group(1)

		playURL= 'http://embed.tune.pk/play/%s?autoplay=no&ssl=no' % playURL.group(2)
		print playURL

		link=getHtml(playURL)
		pattern='file":"(.*?)"'
		match =re.findall(pattern,link)
		print 'match',match
		stream_url=match[0]
		print stream_url
		stream_url=stream_url.replace('\\/','/')
#		stream_url = urlresolver.HostedMediaFile(playURL).resolve()
		return stream_url
	except:
		traceback.print_exc(file=sys.stdout)
		return None

def getHtml(url, ref=None):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link

def SelectUrl(html, url):
	try:
		available_source=[]
		print 'selecting Url'
		mainUrl=getDailyMotionUrl(html,True)
		print 'selected Url: %s' % mainUrl

		if (mainUrl):
			available_source.append('Dailymotion Video')

		mainUrl=getTuneTvUrl(html,True)
		if (mainUrl):
			available_source.append('Tune Video')
			
		mainUrl=getPlaywireUrl(html,True)
		if (mainUrl):
			available_source.append('Playwire Video')
		defaultlinks=['Dailymotion Video', 'Tune Video', 'Playwire Video']
		defaultLinkType=selfAddon.getSetting( "DefaultVideoType" ) 
		if defaultLinkType is None or defaultLinkType == '':
			defaultLinkType='0'
		print defaultLinkType
		defaultLinkType = defaultlinks[int(defaultLinkType)]
		print defaultLinkType

		print 'available_source: %s' % available_source
		if len(available_source)>0:
			return _play_from_available_sources(defaultLinkType, available_source, html)
		else:
			line1 = "No sources found"
			xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, 2000, __icon__))
		return None
	except:
		traceback.print_exc(file=sys.stdout)
		return None

def _play_from_available_sources(defaultLinkType, available_source, html):
	index=0
	if len(available_source)>1:
		print 'defaultLinkType: %s' % defaultLinkType
		if not defaultLinkType in available_source:
			dialog = xbmcgui.Dialog()
			index = dialog.select('Choose your source', available_source)
		else:
			index=available_source.index(defaultLinkType)
	if index > -1:
		linkType=available_source[index]
		line1 = "Finding links from "+linkType
		xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, 2000, __icon__))
		print 'linkType: %s' % linkType

		ret = None

		if 'Dailymotion Video'==linkType:
			ret = getDailyMotionUrl(html,False)
		elif 'Tune Video'==linkType:
			ret = getTuneTvUrl(html,False)
		elif 'Playwire Video'==linkType:
			ret = getPlaywireUrl(html,False)

		if not ret and len(available_source) > 1:
			# try next available source
			available_source.remove(defaultLinkType)

			return _play_from_available_sources(available_source[0], available_source, html)

		return ret

def PlayShowLink ( url ): 
#	url = tabURL.replace('%s',channelName);
	line1 = "Finding links"
	xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, 1000, __icon__))

	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
#	print url
	urlToPlay=SelectUrl(link, url)

	print 'urlToPlay: %s' % urlToPlay

	if urlToPlay:
		playlist = xbmc.PlayList(1)
		playlist.clear()
		listitem = xbmcgui.ListItem(name, iconImage="DefaultVideo.png")
		listitem.setInfo("Video", {"Title":name})
		listitem.setProperty('mimetype', 'video/x-msvideo')
		listitem.setProperty('IsPlayable', 'true')
		playlist.add(urlToPlay,listitem)
		xbmcPlayer = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
		xbmcPlayer.play(playlist)
	return 
	
	line1 = "Playing DM Link"
	time = 5000  #in miliseconds
 	defaultLinkType=0 #0 youtube,1 DM,2 tunepk
	defaultLinkType=selfAddon.getSetting( "DefaultVideoType" ) 
	#print defaultLinkType
	#print "LT link is" ;8+ linkType
	# if linktype is no;t provided then use the defaultLinkType
	linkType="LINK"
	if linkType=="DM" or (linkType=="" and defaultLinkType=="1"):
		#print "PlayDM"
		line1 = "Playing DM Link"
		xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, time, __icon__))
#		print link
		playURL= match =re.findall('src="(.*?(dailymotion).*?)"',link)
		playURL=match[0][0]
		print playURL
		playlist = xbmc.PlayList(1)
		playlist.clear()
		listitem = xbmcgui.ListItem(name, iconImage="DefaultVideo.png")
		listitem.setInfo("Video", {"Title":name})
		listitem.setProperty('mimetype', 'video/x-msvideo')
		listitem.setProperty('IsPlayable', 'true')
		stream_url = urlresolver.HostedMediaFile(playURL).resolve()
		print stream_url
		playlist.add(stream_url,listitem)
		xbmcPlayer = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
		xbmcPlayer.play(playlist)
#src="(.*?(dailymotion).*?)"
	elif  linkType=="LINK"  or (linkType=="" and defaultLinkType=="2"):
		line1 = "Playing Tune.pk Link"
		xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, time, __icon__))

		print "PlayLINK"
		playURL= match =re.findall('<strong>Tune\s*[fU]ull<\/strong>\s*.*?src="(.*?)"', link, re.IGNORECASE)
		print 'playURL',playURL
		if len(playURL)<=0:
			line1 = "Tune not found, trying Daily motion"
			xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, time, __icon__))
			playURL= match =re.findall('<strong>Daily.*.*full.*<\/strong>\s*.*?src="(.*?(daily).*?)"', link,re.IGNORECASE)
		
		if len(playURL)<=0:
			line1 = "Link not found, check the website for Full Tune or Daily motion lists"
			xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, time, __icon__))
			return;
		playURL=match[0]# check if not found then try other methods
		print playURL
		playlist = xbmc.PlayList(1)
		playlist.clear()
		listitem = xbmcgui.ListItem(name, iconImage="DefaultVideo.png")
		listitem.setInfo("Video", {"Title":name})
		listitem.setProperty('mimetype', 'video/x-msvideo')
		listitem.setProperty('IsPlayable', 'true')
		stream_url = urlresolver.HostedMediaFile(playURL).resolve()
		print stream_url
		playlist.add(stream_url,listitem)
		xbmcPlayer = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
	        xbmcPlayer.play(playlist)

#src="(.*?(tune\.pk).*?)"
	else:	#either its default or nothing selected
		line1 = "Playing Youtube Link"
		xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, time, __icon__))
		youtubecode= match =re.findall('<strong>Youtube<\/strong>.*?src=\".*?embed\/(.*?)\?.*\".*?<\/iframe>', link,re.DOTALL| re.IGNORECASE)
		youtubecode=youtubecode[0]
		uurl = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % youtubecode
#	print uurl
		xbmc.executebuiltin("xbmc.PlayMedia("+uurl+")")
	
	return
	


def PlayLiveLink ( url ): 


	progress = xbmcgui.DialogProgress()
	progress.create('Progress', 'Fetching Streaming Info')
	progress.update( 10, "", "Finding links..", "" )

	if mode==7:
		req = urllib2.Request(url)
		req.add_header('User-Agent', 'Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10')
		response = urllib2.urlopen(req)
		link=response.read()
		response.close()
		match =re.findall('"http.*(ebound).*?\?site=(.*?)"',link,  re.IGNORECASE)[0]
		cName=match[1]
		progress.update( 20, "", "Finding links..", "" )

	else:
		cName=url
	#match =re.findall('"http.*(ebound).*?\?site=(.*?)"',link,  re.IGNORECASE)[0]


	
	newURL='http://www.eboundservices.com/iframe/newads/iframe.php?stream='+ cName+'&width=undefined&height=undefined&clip=' + cName
	print newURL

	
	req = urllib2.Request(newURL)
	req.add_header('User-Agent', 'Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	progress.update( 50, "", "Finding links..", "" )

	
#	match =re.findall('<iframe.+src=\'(.*)\' frame',link,  re.IGNORECASE)
#	print match
#	req = urllib2.Request(match[0])
#	req.add_header('User-Agent', 'Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10')
#	response = urllib2.urlopen(req)
#	link=response.read()
#	response.close()
	time = 2000  #in miliseconds
	defaultStreamType=0 #0 RTMP,1 HTTP
	defaultStreamType=selfAddon.getSetting( "DefaultStreamType" ) 
	print 'defaultStreamType',defaultStreamType
	if 1==2 and (linkType=="HTTP" or (linkType=="" and defaultStreamType=="1")): #disable http streaming for time being
#	print link
		line1 = "Playing Http Stream"
		xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, time, __icon__))
		
		match =re.findall('MM_openBrWindow\(\'(.*)\',\'ebound\'', link,  re.IGNORECASE)
			
	#	print url
	#	print match
		
		strval = match[0]
		
		#listitem = xbmcgui.ListItem(name)
		#listitem.setInfo('video', {'Title': name, 'Genre': 'Live TV'})
		#playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
		#playlist.clear()
		#playlist.add (strval)
		
		#xbmc.Player().play(playlist)
		listitem = xbmcgui.ListItem( label = str(cName), iconImage = "DefaultVideo.png", thumbnailImage = xbmc.getInfoImage( "ListItem.Thumb" ), path=strval )
		print "playing stream name: " + str(cName) 
		listitem.setInfo( type="video", infoLabels={ "Title": cName, "Path" : strval } )
		listitem.setInfo( type="video", infoLabels={ "Title": cName, "Plot" : cName, "TVShowTitle": cName } )
		xbmc.Player(PLAYER_CORE_AUTO).play( str(strval), listitem)
	else:
		line1 = "Playing RTMP Stream"
		xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line1, time, __icon__))
		progress.update( 60, "", "Finding links..", "" )

		post = {'username':'hash'}
        	post = urllib.urlencode(post)
		req = urllib2.Request('http://eboundservices.com/flashplayerhash/index.php')
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36')
		response = urllib2.urlopen(req,post)
		link=response.read()
		response.close()
		

        
		print link
		#match =re.findall("=(.*)", link)

		#print url
		#print match

		strval =link;# match[0]

		#listitem = xbmcgui.ListItem(name)
		#listitem.setInfo('video', {'Title': name, 'Genre': 'Live TV'})
		#playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
		#playlist.clear()
		#playlist.add (strval)

		playfile='rtmp://cdn.ebound.tv/tv?wmsAuthSign=/%s app=tv?wmsAuthSign=?%s swfurl=http://www.eboundservices.com/live/v6/player.swf?domain=&channel=%s&country=GB pageUrl=http://www.eboundservices.com/iframe/newads/iframe.php?stream=%s tcUrl=rtmp://cdn.ebound.tv/tv?wmsAuthSign=?%s live=true timeout=15'	% (cName,strval,cName,cName,strval)
		#playfile='rtmp://cdn.ebound.tv/tv?wmsAuthSign=/humtv app=tv?wmsAuthSign=?%s swfurl=http://www.eboundservices.com/live/v6/player.swf?domain=&channel=humtv&country=GB pageUrl=http://www.eboundservices.com/iframe/newads/iframe.php?stream=humtv tcUrl=rtmp://cdn.ebound.tv/tv?wmsAuthSign=?%s live=true'	% (strval,strval)
		progress.update( 100, "", "Almost done..", "" )
		print playfile
		#xbmc.Player().play(playlist)
		listitem = xbmcgui.ListItem( label = str(name), iconImage = "DefaultVideo.png", thumbnailImage = xbmc.getInfoImage( "ListItem.Thumb" ) )
		print "playing stream name: " + str(name) 
		#listitem.setInfo( type="video", infoLabels={ "Title": name, "Path" : playfile } )
		#listitem.setInfo( type="video", infoLabels={ "Title": name, "Plot" : name, "TVShowTitle": name } )
		xbmc.Player( xbmc.PLAYER_CORE_AUTO ).play( playfile, listitem)
		#xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)

	return

	
#print "i am here"
params=get_params()
url=None
name=None
mode=None
linkType=None

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


args = cgi.parse_qs(sys.argv[2][1:])
linkType=''
try:
	linkType=args.get('linkType', '')[0]
except:
	pass


print 'mode: %s' % mode

try:
	if mode==None or url==None or len(url)<1:
		print "InAddTypes"
		Addtypes()

	elif mode==2:
		print "Ent url is "+name,url
		AddSeries(url)

	elif mode==3:
		print "Ent url is "+url
		AddEnteries(url)

	elif mode==4:
		print "Play url is "+url
		PlayShowLink(url)

	elif mode==5:
		print "TopRatedDramas url is "+url
		TopRatedDramas(url)
	elif mode==6:
		print "Play url is "+url
		addDir(Colored('DramasOnline Channels','ZM',True) ,'ZEMTV' ,10,'', False, True,isItFolder=False)		#name,url,mode,icon
		AddChannels(url)
		addDir(Colored('EboundServices Channels','EB',True) ,'ZEMTV' ,10,'', False, True,isItFolder=False)		#name,url,mode,icon		
		AddChannelsFromEbound()
	elif mode==7 or mode==9:
		print "Play url is "+url,mode
		PlayLiveLink(url)
	elif mode==8:
		print "Play url is "+url,mode
		ShowSettings(url)
except:
	print 'somethingwrong'

if not ( mode==7 or mode==4 or mode==9):
	xbmcplugin.endOfDirectory(int(sys.argv[1]))
