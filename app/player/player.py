import vlc
import threading
import random
import os

class Player:
	def __init__(self):		
		# self.mprisManager = mprisManager
		self.vlc = vlc.Instance('-q > /dev/null 2>&1')
		self.playlist = []
		self.currentItem = 0
		self.player = None
		self.event_manager = None
		self.currentPosition = 0	
		self.isPlaying = False	
		self.mediaItem = 0
		self.preloadIndices = []
		self.loop = False

		self.loopFile = os.getcwd() + '/loop'
		self.readLoop()


	def readLoop(self):
		if (os.path.isfile(self.loopFile)):
			f = open(self.loopFile, "r")
			if (f.read() == "1"):
				self.loop = True
			f.close()

	def start(self, track, playlist=None):
		self.preloadIndices = []
		if self.playlist == None:			
			self.playlist = [ track ]
			self.currentItem = 0
		else:			
			self.playlist = playlist.copy()
			self.currentItem = self.playlist.index(track)			

		if (self.player == None):
			self.player = self.vlc.media_player_new()
			self.event_manager = self.player.event_manager()	
			self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached,      self.end_callback)
			self.event_manager.event_attach(vlc.EventType.MediaPlayerPositionChanged, self.pos_callback, self.player)	

		self.setMediaAsync(self.playlist[self.currentItem])		

	def shuffle(self):
		if (self.player == None):
			return

		self.stop()
		random.shuffle(self.playlist)
		self.currentItem = 0
		self.currentPosition = 0
		self.setMediaAsync(self.playlist[self.currentItem], play=True)


	def nextTrack(self):		
		self.pause()
		self.currentItem = self.currentItem + 1
		shouldPlay = True
		if (len(self.playlist) <= self.currentItem):			
			self.currentItem = 0			
			if (not self.loop):
				shouldPlay = False		

		self.setMediaAsync(self.playlist[self.currentItem], play=shouldPlay)

	def prevTrack(self):

		self.pause()
		self.currentItem = self.currentItem - 1
		if (self.currentItem < 0):
			self.currentItem = 0

		self.setMediaAsync(self.playlist[self.currentItem])

	def getTrack(self, index=-1):
		if index == -1:
			index = self.currentItem
		try:
			if (len(self.playlist) == 0):
				return None

			return self.playlist[index]
		except:
			return None

	def setMedia(self, uri):
		if (self.player == None):
			return

		self.player.set_media(self.vlc.media_new(uri))
		self.mprisManager.event_handler.on_app_event('setMedia')

	def getPosition(self):
		return self.player.get_position()

	def pause(self):
		if (self.player == None):
			return

		self.isPlaying = False
		if (self.player.is_playing()):
			self.player.pause()
		self.mprisManager.event_handler.on_app_event('pause')

	def play(self):
		if (self.player == None):
			return
		self.player.play()
		self.isPlaying = True
		self.mprisManager.event_handler.on_app_event('play')

	def stop(self):
		if (self.player == None):
			return
		self.isPlaying = False
		self.player.stop()
		self.currentItem = 0
		self.currentPosition = 0
		self.setMediaAsync(self.playlist[self.currentItem], play=False)
		self.mprisManager.event_handler.on_app_event('stop')

	def end_callback(self, event):		
		self.nextTrack()
	
	def pos_callback(self, event, player):        		
		self.currentPosition = event.u.new_position
		self.mprisManager.event_handler.on_app_event('positionChanged')
		if self.currentPosition > 0.6:
			self.preloadNextTrack()

	def setMediaAsync(self, track, play=True):
		thread = threading.Thread(target=setMediaAsyncWorker, args=(track, self, play,))
		thread.start()

	def preloadNextTrack(self):
		index = self.currentItem + 1

		if ((len(self.playlist) <= index) or (index in self.preloadIndices)):								
			return

		track = self.playlist[index]
		self.preloadIndices.append(index)
		thread = threading.Thread(target=preloadTrackWorker, args=(track,))
		thread.start()

	def setLoop(self, value=True):
		self.loop = value
		f = open(self.loopFile, "w")
		if self.loop:
			f.write("1")
		else:
			f.write("0")
		f.close()



def preloadTrackWorker(track):
	track.getUri()

def setMediaAsyncWorker(track, player, play):
	player.mediaItem = player.playlist.index(track)
	
	uri = None
	attempt = 0
	maxAttempts = 5
	while attempt < maxAttempts:
		attempt = attempt + 1
		try:
			uri = track.getUri()
			break
		except Exception as e:
			print(e)

	if (uri == None):
		player.nextTrack()
		return

	player.setMedia(uri)		
	if (play == True):
		player.play()		




player = Player()