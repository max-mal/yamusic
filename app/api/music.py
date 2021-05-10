from yandex_music.client import Client, Artist, Track, Playlist, Album
from ..database.storage import storage
import os

class MusicClient:
	def __init__(self):        
		self.token = None
		self.client = None
		self.loggedIn = False   
		self.online = False     
		self.ui = None   		
		
	def init(self):        
		if os.path.isfile('token.txt'):
			try:
				tokenFile = open('token.txt', 'r')
				self.token = tokenFile.read()
				tokenFile.close();
				self.client = Client(self.token)
				self.loggedIn = True
				self.online = True
			except:                
				return False
				
		else:
			return False
		
		return True
	def auth(self, login, password):
		try:
			self.client = Client.from_credentials(login, password, captcha_callback=self.proc_captcha)        
			tokenFile = open('token.txt', 'w')
			tokenFile.write(self.client.token)
			tokenFile.close();
			self.loggedIn = True
			return True
		except Exception as e:
			return False

	def proc_captcha(self, captcha):
		captcha.download('captcha.png')
		if os.system("./captcha.png") != 0:
			os.system("xdg-open ./captcha.png")
		return input('Число с картинки: ')

	def getFeedPlaylists(self):
		playlists = self.client.feed().generated_playlists

		return storage.savePlaylists(playlists, is_feed=1)

	def getPlaylistTracks(self, playlist):
		p = self.client.playlists_list( [playlist.id] )
		if (len(p) == 0):
			return[]

		clientPlaylist = p[0]
		return storage.saveTracks(clientPlaylist.fetchTracks(), playlist=playlist)

	def getUri(self, track):
		if not self.online:
			return None

		if (track._directLink != None):
			return track._directLink

		try:                                
			trackInfo = self.client.tracks_download_info(track.id, True)              
			for info in trackInfo:
				if info.codec == "mp3" and info.bitrate_in_kbps == 192:
					# info.get_direct_link()
					track._directLink = info.direct_link
					return track._directLink
		except Exception as e:
			raise e
			print("Cannot get track info. " + str(e))

		return None

	def downloadTrack(self, track):
		if not self.online:
			return None

		trackInfo = self.client.tracks_download_info(track.id, True)              
		for info in trackInfo:
			if info.codec == "mp3" and info.bitrate_in_kbps == 192:
				info.download(track.getDownloadsDirectory() + '/' + track.generateFilename())
				track.is_downloaded = 1
				track.filename = track.generateFilename()
				track.store()

	def getArtistTracks(self, artist, page=0, pageSize=20):
		data = self.client.artists_tracks(artist.id, page, pageSize)			
		return storage.saveTracks(data.tracks)

	def getArtistAlbums(self, artist):
		albums = []
		page = 0
		pageSize = 20
		maxPage = 1

		while page < maxPage:
			data = self.client.artists_direct_albums(artist.id, page, pageSize)
			maxPage = (data.pager.total // pageSize) + 1
			albums.extend(data.albums)
			page = page + 1

		return storage.saveAlbums(albums)

	def getAlbumTracks(self, album):
		data = self.client.albums_with_tracks(album.id)
		tracks = []		
		for arr in data.volumes:
			tracks.extend(arr)

		return storage.saveTracks(tracks)

	def search(self, query):
		data = self.client.search(query)		
		response = {
			"best": None,
			"best_type": None,
			"tracks": [],
			"albums": [],
			"artists": [],
			"playlists": [],
		}

		tracks = data.tracks.results
		albums = data.albums.results
		artists = data.artists.results
		playlists = data.playlists.results

		print(list(tracks), file=open('a1.log', 'w'))

		response['tracks'] = storage.saveTracks(tracks)
		response['albums'] = storage.saveAlbums(albums)
		response['artists'] = storage.saveArtists(artists)
		response['playlists'] = storage.savePlaylists(playlists)

		best = None
		if (data.best.type == 'track'):
			best = storage.saveTracks([data.best.result])[0]
			response['best_type'] = 'track'

		if (data.best.type == 'artist'):
			best = storage.saveArtists([data.best.result])[0]
			response['best_type'] = 'artist'

		if (data.best.type == 'playlist'):
			best = storage.savePlaylists([data.best.result])[0]
			response['best_type'] = 'playlist'

		if (data.best.type == 'album'):
			best = storage.saveAlbums([data.best.result])[0]
			response['best_type'] = 'album'

		response['best'] = best

		return response

	def likeTrack(self, track):
		if (track.is_liked == 1):
			self.client.users_likes_tracks_remove(track.id)
			track.is_liked = 0
		else:
			self.client.users_likes_tracks_add(track.id)
			track.is_liked = 1

		track.is_disliked = 0
		track.store()

	def dislikeTrack(self, track):
		if (track.is_disliked == 1):
			self.client.users_dislikes_tracks_remove(track.id)
			track.is_disliked = 0
		else:
			self.client.users_dislikes_tracks_add(track.id)
			track.is_disliked = 1

		track.is_liked = 0		
		track.store()

	def getLikedTracks(self):
		tracks = self.client.users_likes_tracks().fetch_tracks()
		return storage.saveTracks(tracks, isLiked=True)


music = MusicClient()
music.init()

	
