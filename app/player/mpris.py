# import gi
# gi.require_version('Gst', '1.0')

import threading
from mpris_server.adapters import MprisAdapter
from mpris_server.events import EventAdapter
from mpris_server.server import Server
from mpris_server.base import Metadata, Track, PlayState, Microseconds, VolumeDecimal, RateDecimal, DEFAULT_RATE, Artist
from .player import player


class MyAppAdapter(MprisAdapter):

	# def metadata(self) -> Metadata:
	# 	return {
	# 		"mpris:trackid": "/track/1",
	# 		"mpris:length": 1000000,
	# 		"mpris:artUrl": "Example",
	# 		"xesam:url": "https://google.com",
	# 		"xesam:title": "Example title",
	# 		"xesam:artist": ["My Awesome artist"],
	# 		"xesam:album": "Album name",
	# 		"xesam:albumArtist": [],
	# 		"xesam:discNumber": 1,
	# 		"xesam:trackNumber": 1,
	# 		"xesam:comment": [],
	# 	}
	def get_current_track(self) -> Track:
		track = player.getTrack()
		if track == None:
			return None

		return Track(
			track_id='/track/' + str(track.id), 
			name=track.title, 
			length=track.duration * 1000, 
			artists=tuple(map(lambda artist: Artist(artist.name), track._artists))
		)

	def get_current_position(self) -> Microseconds:
		return player.currentPosition * 1000

	def next(self):		
		player.nextTrack()

	def previous(self):
		player.prevTrack()

	def pause(self):		
		player.pause()
	
	def resume(self):
		player.play()

	def stop(self):
		player.stop()

	def play(self):		
		player.play()

	def get_playstate(self) -> PlayState:		
		if player.isPlaying == True:			
			return PlayState.PLAYING
		else:			
			return PlayState.PAUSED

	def seek(self, time: Microseconds):
		event_handler.on_app_event('seekTo', time)


	def open_uri(self, uri: str):
		print('open_uri ' + uri)

	def is_repeating(self) -> bool:
		return False

	def is_playlist(self) -> bool:
		return False

	def set_repeating(self, val: bool):
		pass

	def set_loop_status(self, val: str):
		player.loop = val

	def get_rate(self) -> RateDecimal:
		return DEFAULT_RATE

	def set_rate(self, val: RateDecimal):
		pass

	def get_shuffle(self) -> bool:
		return False

	def set_shuffle(self, val: bool):
		player.shuffle()

	def get_art_url(self, track: int) -> str:
		return 'http://noneurl.com'

	def get_volume(self) -> VolumeDecimal:
		return 1.0

	def set_volume(self, val: VolumeDecimal):
		pass

	def is_mute(self) -> bool:
		return False

	def set_mute(self, val: bool):
		pass

	def can_go_next(self) -> bool:
		return True

	def can_go_previous(self) -> bool:
		return True

	def can_play(self) -> bool:
		return True

	def can_pause(self) -> bool:
		return True

	def can_seek(self) -> bool:
		return False

	def can_control(self) -> bool:
		return True

	def get_stream_title(self) -> str:
		track = player.getTrack()
		if track != None:
			return track.title

		return ''

	def get_previous_track(self) -> Track:
		track = player.getTrack(player.currentItem - 1)
		if track == None:
			return None

		return Track(
			track_id='/track/' + str(track.id), 
			name=track.title, 
			length=track.duration * 1000, 
			artists=tuple(map(lambda artist: Artist(artist.name), track._artists))
		)	

	def get_next_track(self) -> Track:
		track = player.getTrack(player.currentItem + 1)
		if track == None:
			return None

		return Track(
			track_id='/track/' + str(track.id), 
			name=track.title, 
			length=track.duration * 1000, 
			artists=tuple(map(lambda artist: Artist(artist.name), track._artists))
		)


class MyAppEventHandler(EventAdapter):
	# EventAdapter has good default implementations for its methods.
	# Only override the default methods if it suits your app.

	def on_app_event(self, event: str):		
		if event == 'pause':	
			self.on_playpause()
		if event == 'play':
			self.on_playpause()
		if event == 'stop':
			self.on_playpause()
		if event == 'setMedia':
			self.on_title()
			# self.on_playlist_change()
		# if event == 'positionChanged':
		# 	self.on_seek(player.currentPosition * 1000)




# create mpris adapter and initialize mpris server
# my_adapter = MyAppAdapter()
# mpris = Server('MyApp', adapter=my_adapter)
# event_handler = MyAppEventHandler(root=mpris.root, player=mpris.player)
# mpris.loop()

class PlayerMpris:
	def __init__(self):
		self.adapter = MyAppAdapter()
		self.server = Server('YaMusicPlayer', adapter=self.adapter)
		self.event_handler = MyAppEventHandler(root=self.server.root, player=self.server.player)

	def start(self):
		thread = threading.Thread(target=mprisWorker, args=(self,), daemon=True)
		thread.start()


def mprisWorker(manager):
	manager.server.loop()


mprisManager = PlayerMpris()
mprisManager.start()

player.mprisManager = mprisManager