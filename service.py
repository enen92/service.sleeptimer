#!/usr/bin/python
import time
import datetime
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
import json

# changed to "idle.time"

addon_id = 'service.safestop'
selfAddon = xbmcaddon.Addon(id=addon_id)
datapath = xbmc.translatePath(selfAddon.getAddonInfo('profile')).decode('utf-8')
addonfolder = xbmc.translatePath(selfAddon.getAddonInfo('path')).decode('utf-8')
#msgok = xbmcgui.Dialog().ok
msgdialogprogress = xbmcgui.DialogProgress()

debug=selfAddon.getSetting('debug_mode')
check_time = int(selfAddon.getSetting('check_time'))
max_time_in_minutes = int(selfAddon.getSetting('max_time'))
time_to_wait = int(selfAddon.getSetting('waiting_time_dialog'))
audiochange = selfAddon.getSetting('audio_change')

class service:
	def __init__(self):
		intro = False
		next_check = False
		while not xbmc.abortRequested:
			if not intro:
				print "service.safestop: started..."
				intro = True

			idle_time = xbmc.getGlobalIdleTime()
			idle_time_in_minutes = int(idle_time)/60

			if xbmc.Player().isPlaying():

				#if debug == 'true':
					#print "service.safestop: max_time_in_minutes before calculation: " + str(max_time_in_minutes)

				if next_check == 'true':
					# add "diff_betwenn_idle_and_check_time" to "idle_time_in_minutes"
					idle_time_in_minutes += int(diff_betwenn_idle_and_check_time)

				#if debug == 'true':
					#print "service.safestop: max_time_in_minutes after calculation: " + str(max_time_in_minutes)

				if xbmc.Player().isPlayingAudio():
					print "service.safestop: Player is playing Audio"
				elif xbmc.Player().isPlayingVideo():
					print "service.safestop: Player is playing Video"
				else:
					print "service.safestop: Player is playing, but no Audio or Video"
				
				#executeJSONRPC(jsonrpccommand)--Execute an JSONRPC command.
				#jsonrpccommand : string - jsonrpc command to execute.
				#List of commands -
				#example:
				#- response = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "JSONRPC.Introspect", "id": 1 }')
				
				#executebuiltin(function)--Execute a built in XBMC function.
				#function : string - builtin function to execute.
				#List of functions -http://kodi.wiki/view/List_of_Built_In_Functions 
				#example:
				#- xbmc.executebuiltin('RunXBE(c:\avalaunch.xbe)')

				# only for debugging:
				max_time_in_minutes = 2

				if debug == 'true':
					print "service.safestop: idle_time: '" + str(idle_time) + "s'; idle_time_in_minutes: '" + str(idle_time_in_minutes) + "'"
					print "service.safestop: max_time_in_minutes: " + str(max_time_in_minutes)
				if idle_time_in_minutes >= max_time_in_minutes:
					if debug == 'true':
						print "service.safestop: idle_time exceeds max allowed. Display Progressdialog"
					ret = msgdialogprogress.create("Safe Stop","Cancel to continue watching")
					secs=0
					percent=0
					# use the multiplier 100 to get better results: 
					increment = 100*100 / time_to_wait
					cancelled = False
					while secs < time_to_wait:
						secs = secs + 1
						# divide with 100, to get the right value
						percent = increment*secs/100
						#print "service.safestop: percent: " + str(percent)
						#print "service.safestop: percent_int: " + str(percent_int)
						secs_left = str((time_to_wait - secs))
						remaining_display = str(secs_left) + " seconds left."
						msgdialogprogress.update(percent,"Cancel to continue watching",remaining_display)
						xbmc.sleep(1000)
						if (msgdialogprogress.iscanceled()):
							cancelled = True
							print "service.safestop: Progressdialog cancelled"
							break
					if cancelled == True:
						print "service.safestop: Progressdialog closed"
						check_time = int(selfAddon.getSetting('check_time_next'))
						if debug == 'true':
							print "service.safestop: cancelled true: check_time: " + str(check_time)
						# set next_check, so that it opens the dialog after "check_time"
						next_check = True
						msgdialogprogress.close()
					else:
						print "service.safestop: not cancelled: stopping Player"
						msgdialogprogress.close()

						# softmute audio before stop playing
						# source: http://www.kodinerds.net/index.php/Thread/39369-Softmute/
						# get actual volume
						if audiochange == 'true':
							resp = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Application.GetProperties", "params": { "properties": [ "volume"] }, "id": 1}')
							dct = json.loads(resp)
							muteVol = 10

							if (dct.has_key("result")) and (dct["result"].has_key("volume")):
								curVol = dct["result"]["volume"]
								# print "service.safestop: actual Volume: " + str(curVol)
								
								for i in range(curVol - 1, muteVol - 1, -1):
									# print "service.safestop: set Volume to " + str(i)
									xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Application.SetVolume", "params": { "volume": %d }, "id": 1}' %(i) )
									# move down slowly
									xbmc.sleep(500)

						# stop player anyway
						xbmc.Player().stop()

						if audiochange == 'true':
							xbmc.sleep(2000) # wait 2s before changing the volume back
							if (dct.has_key("result")) and (dct["result"].has_key("volume")):
								curVol = dct["result"]["volume"]
								# print "service.safestop: set Volume to " + str(curVol)
								# we can move upwards fast, because there is nothing playing
								xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Application.SetVolume", "params": { "volume": %d }, "id": 1}' %(curVol) )
								# xbmc.executebuiltin(SetVolume(percent[,showvolumebar]))
				else:
					check_time = int(selfAddon.getSetting('check_time'))
					if debug == 'true':
						print "service.safestop: Playing the stream, time does not exceed max limit"
			else:
				if debug == 'true':
					print "service.safestrop: Not playing any media file"
				check_time = int(selfAddon.getSetting('check_time'))
			
			diff_between_idle_and_check_time = idle_time_in_minutes - check_time
			if debug == 'true' and next_check == 'true':
				print "service.safestop: diff_between_idle_and_check_time: " + str(diff_between_idle_and_check_time)
			
			xbmc.sleep(check_time*60*1000)

service()