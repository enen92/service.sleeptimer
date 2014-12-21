#!/usr/bin/python
import time
import datetime
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs

addon_id = 'service.safestop'
selfAddon = xbmcaddon.Addon(id=addon_id)
datapath = xbmc.translatePath(selfAddon.getAddonInfo('profile')).decode('utf-8')
addonfolder = xbmc.translatePath(selfAddon.getAddonInfo('path')).decode('utf-8')
msgok = xbmcgui.Dialog().ok
mensagemprogresso = xbmcgui.DialogProgress()

debug=selfAddon.getSetting('debug_mode')
check_time = int(selfAddon.getSetting('check_time'))
max_time = int(selfAddon.getSetting('max_time'))
time_to_wait = int(selfAddon.getSetting('waiting_time_dialog'))

class service:
	def __init__(self):
		intro = False
		while not xbmc.abortRequested:
			if not intro:
				print "service.safestop"
				print "Service started..."
				intro = True
			
			if xbmc.Player().isPlaying():
				playback_time = xbmc.Player().getTime()
				if int(playback_time)/(60*60) >= max_time:
					if debug == 'true':
						print "service.safestop: Time exceeds max allowed. Stopping the stream"
						ret = mensagemprogresso.create('Safe Stop')
						secs=0
						percent=0
						increment = int(100 / time_to_wait)
						cancelled = False
						while secs < time_to_wait:
							secs = secs + 1
							percent = increment*secs
							secs_left = str((time_to_wait - secs))
							remaining_display = str(secs_left) + " seconds left."
							mensagemprogresso.update(percent,"Cancel to continue watching",remaining_display)
							xbmc.sleep(1000)
							if (mensagemprogresso.iscanceled()):
								cancelled = True
								break
						if cancelled == True:
							check_time = int(selfAddon.getSetting('check_time_next'))
						else:
							mensagemprogresso.close()
							xbmc.Player().stop()
				else:
					check_time = int(selfAddon.getSetting('check_time'))
					if debug == 'true':
						print "service.safestop: Playing the stream, time does not exceed max limit"
						
			else:
				if debug == 'true':
					print "service.safestrop: Not playing any media file"
				check_time = int(selfAddon.getSetting('check_time'))


			xbmc.sleep(check_time*60*1000)

service()


