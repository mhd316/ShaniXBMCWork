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


profile_path =  xbmc.translatePath(selfAddon.getAddonInfo('profile'))
def PlayStream(sourceEtree, urlSoup, name, url):
	try:
		channelId = urlSoup.url.text
		pDialog = xbmcgui.DialogProgress()
		pDialog.create('XBMC', 'Communicating with SS')
		import base64
		if 1==1:
			liveLink=base64.b64decode('aHR0cDovLzQ2LjEwMS45LjIyNi82MC9jaCVzL2luZGV4Lm0zdTg=')%channelId
			pDialog.create('XBMC', 'Playing channel')
			listitem = xbmcgui.ListItem( label = str(name), iconImage = "DefaultVideo.png", thumbnailImage = xbmc.getInfoImage( "ListItem.Thumb" ), path=liveLink )
			player = CustomPlayer.MyXBMCPlayer()
			start = time.time()  
			player.pdialogue=pDialog
			if pDialog.iscanceled():
				return True
			player.play( liveLink,listitem)  
			if pDialog.iscanceled():
				return True
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


